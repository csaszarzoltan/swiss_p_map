"""Unit tests for BFS Federal Vote Service (ADR-012).

SPEC-056b honesty contract (FR-02, measured 2026-10-05): on a SUCCESSFUL live
refresh the served proposal set is ONLY the live result — the four embedded
2024 fixture proposals (6670/6680/6690/6700) are no longer merged into the
served set, because ``trust_state`` is per-response and a response cannot
honestly be both "official_publication" and "embedded fixture". On FAILURE
the fixtures are STILL served but labelled ``trust_state: "stale"``.
"""

from __future__ import annotations

import httpx
import pytest

from fastapi.testclient import TestClient

from src.main import app
from src.services.vote_service import BFS_CANTON_MAP, VoteService

_FIXTURE_IDS = (6670, 6680, 6690, 6700)


class TestVoteService:
    @pytest.mark.test_id("TEST-VOTE-001")
    @pytest.mark.requirements("ADR-012")
    @pytest.mark.scenario("AC1: BFS canton map covers all 26 cantons.")
    def test_canton_map_covers_all_26_cantons(self) -> None:
        """Mind a 26 svájci kanton szerepel a BFS kód-leképezésben."""
        assert len(BFS_CANTON_MAP) == 26
        expected_cantons = {
            "ZH",
            "BE",
            "LU",
            "UR",
            "SZ",
            "OW",
            "NW",
            "GL",
            "ZG",
            "FR",
            "SO",
            "BS",
            "BL",
            "SH",
            "AR",
            "AI",
            "SG",
            "GR",
            "AG",
            "TG",
            "TI",
            "VD",
            "VS",
            "NE",
            "GE",
            "JU",
        }
        assert set(BFS_CANTON_MAP.values()) == expected_cantons

    @pytest.mark.test_id("TEST-VOTE-002")
    @pytest.mark.requirements("ADR-012")
    @pytest.mark.scenario("AC2: seed proposal exposes all 26 cantons and four-language titles.")
    def test_get_latest_vote_contains_all_cantons(self) -> None:
        """A legfrissebb szavazás tartalmazza mind a 26 kanton eredményét és a 4 nyelvű címet."""
        service = VoteService()
        proposal = service.get_latest_vote()

        assert proposal is not None
        assert proposal.proposal_id > 0
        assert proposal.date != ""
        assert "de" in proposal.titles
        assert "fr" in proposal.titles
        assert "it" in proposal.titles
        assert "en" in proposal.titles
        assert 0.0 <= proposal.national_yes_percent <= 100.0
        assert 0.0 <= proposal.national_turnout_percent <= 100.0
        assert len(proposal.cantons) == 26

        # Ellenőrizzük Zürich és Bern értékeit
        zh = proposal.cantons.get("ZH")
        assert zh is not None
        assert zh.canton == "ZH"
        assert abs(zh.yes_percent + zh.no_percent - 100.0) < 0.2

        be = proposal.cantons.get("BE")
        assert be is not None
        assert be.canton == "BE"
        assert abs(be.yes_percent + be.no_percent - 100.0) < 0.2

    @pytest.mark.test_id("TEST-VOTE-003")
    @pytest.mark.requirements("ADR-012")
    @pytest.mark.scenario("AC3: GET votes/latest returns 200 with top-level proposal shape.")
    def test_vote_endpoint_returns_200(self) -> None:
        """A /api/v1/politics/votes/latest végpont 200-as választ és érvényes struktúrát ad."""
        client = TestClient(app)
        resp = client.get("/api/v1/politics/votes/latest")
        assert resp.status_code == 200
        data = resp.json()
        assert "proposal_id" in data
        assert "titles" in data
        assert "cantons" in data
        assert "ZH" in data["cantons"]
        assert "BE" in data["cantons"]
        assert "GE" in data["cantons"]

    @pytest.mark.test_id("TEST-VOTE-004")
    @pytest.mark.requirements("SPEC-056b:FR-02,FR-03")
    @pytest.mark.scenario(
        "AC4: on a successful live refresh the served set is only the live result, never the fixtures."
    )
    def test_vote_proposals_list_and_detail(self) -> None:
        """A live sikeres frissítés után a served set CSAK az élő eredmény (ADR-017, SPEC-056b FR-02).

        The live OGD publication for vote day 20260927 genuinely carries ONE
        proposal. Serving one item under ``trust_state: official_publication``
        is honest; the number 4 came from this repo's own fixture constants.
        """
        client = TestClient(app)
        resp = client.get("/api/v1/politics/votes/list")
        assert resp.status_code == 200
        body = resp.json()
        assert "items" in body, "votes/list must return 'items' at the top level"
        items = body.get("items", [])
        assert isinstance(items, list) and len(items) >= 1, (
            f"served set must be non-empty, got {items!r}"
        )
        # Envelope travels on the success path.
        for key in ("source", "fetched_at", "trust_state"):
            assert key in body, f"envelope key {key!r} missing from votes/list"
        # REGRESSION (binding gate): on success the served set must contain
        # ONLY live ids — none of the four fixture ids may appear under
        # official_publication.
        if body.get("trust_state") == "official_publication":
            ids = [p["proposal_id"] for p in items]
            for fid in _FIXTURE_IDS:
                assert fid not in ids, (
                    f"fixture id {fid} must never be served as live "
                    f"under official_publication — served ids: {ids}"
                )

        # Detail lookup for the first LIVE-served proposal.
        live_id = items[0]["proposal_id"]
        detail_resp = client.get(f"/api/v1/politics/votes/{live_id}")
        assert detail_resp.status_code == 200
        detail_data = detail_resp.json()
        assert "national_yes_percent" in detail_data, (
            "detail must expose national_yes_percent"
        )
        for key in ("source", "fetched_at", "trust_state"):
            assert key in detail_data, f"envelope key {key!r} missing from detail"

        # 404 for unknown proposal — unchanged.
        err_resp = client.get("/api/v1/politics/votes/99999")
        assert err_resp.status_code == 404

    @pytest.mark.asyncio
    @pytest.mark.test_id("TEST-VOTE-005")
    @pytest.mark.requirements("SPEC-056b:FR-04")
    @pytest.mark.scenario(
        "AC5: on a failed refresh the four 2024 fixtures are still served, labelled stale."
    )
    async def test_vote_list_failure_path_serves_fixtures_as_stale(self) -> None:
        """A sikertelen frissítés után a fixture-ök továbbra is elérhetők — stale címkével."""

        def server_error(request: httpx.Request) -> httpx.Response:
            return httpx.Response(500, json={"error": "internal"})

        transport = httpx.MockTransport(server_error)
        async with httpx.AsyncClient(transport=transport) as http_client:
            svc = VoteService(client=http_client)
            ok = await svc.refresh_from_live(vote_date="20260927")
            assert ok is False, "forced 500 must degrade to False"
            assert svc.trust_state == "stale", (
                f"fixtures present → trust_state must be 'stale', got {svc.trust_state!r}"
            )
            served = {p["proposal_id"] for p in svc.list_proposals()}
            for fid in _FIXTURE_IDS:
                assert fid in served, (
                    f"fixture id {fid} must still be served on the failure path — served: {sorted(served)}"
                )
            # The BVG fixture content stays pinned HERE (it is honest under stale).
            bvg = svc.get_proposal_by_id(6680)
            assert bvg is not None
            assert bvg.national_yes_percent == 32.9
            assert bvg.cantons["ZH"].yes_percent == 34.8
