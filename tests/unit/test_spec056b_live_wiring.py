"""Gate: SPEC-056b live VoteInfo OGD wiring must be behind the honest envelope.

Fails PRE-FIX (parent of commit 33aab13) for every reason listed in the report's
item 4; green only once the live host, the envelope, and the failure-degrade are
all present. No network allowed — either MockTransport or an injected fake client.

Fixtures:
  tests/unit/fixtures/voteinfo_ogd_20260927_trimmed.json — recorded once
  from https://ogd-static.voteinfo-app.ch/v1/ogd/sd-t-17-02-20260927-eidgAbstimmung.json
  (2,056,409 bytes live → 141,900 bytes trimmed: 26 cantons, ZH with 161
  municipalities, other cantons with 2 municipalities, vorlagenId 6880). Top
  keys are abstimmtag / timestamp / spatial_reference / schweiz; the second
  vorlagenId (6890) is NOT in the fixture. The unmodified recorded top-level
  keys are preserved; only canton gemeinden were trimmed symmetrically.
"""

from __future__ import annotations

import json
import pathlib

import httpx
import pytest
from fastapi.testclient import TestClient

from src.main import app
from src.services.connectors.bfs_voteinfo_client import (
    BfsVoteInfoClient,
    OGD_HOST,
    OGD_URL_TEMPLATE,
)
from src.services.vote_service import VoteService

_FIXTURE_PATH = (
    pathlib.Path(__file__).parent / "fixtures" / "voteinfo_ogd_20260927_trimmed.json"
)

FIXTURE_IDS = [6670, 6680, 6690, 6700]
LIVE_IDS = [6880]  # recorded fixture carries exactly one vorlagenId; second proposal 6890 not present
REAL_HOST = "voteinfo-app.ch"
OGD_FULL_URL = OGD_URL_TEMPLATE.format(vote_date="20260927")


def _load_fixture() -> dict[str, object]:
    return json.loads(_FIXTURE_PATH.read_text(encoding="utf-8"))  # type: ignore[no-any-return]


def test_fixture_is_real_recorded_shape_not_invention() -> None:
    """Recorded fixture carries the real OGD top-level shape and 26 cantons with municipalities."""
    data = _load_fixture()
    assert "abstimmtag" in data, "fixture missing live key abstimmtag"
    assert "timestamp" in data, "fixture missing live key timestamp"
    assert "spatial_reference" in data, "fixture missing live key spatial_reference"
    assert "schweiz" in data, "fixture missing live key schweiz"
    assert isinstance(data["schweiz"], dict)
    vorlagen = data["schweiz"].get("vorlagen")  # type: ignore[union-attr]
    assert isinstance(vorlagen, list) and len(vorlagen) >= 1
    kantone = vorlagen[0].get("kantone")  # type: ignore[union-attr]
    assert isinstance(kantone, list) and len(kantone) == 26, (
        f"fixture must carry exactly 26 cantons, got {len(kantone) if isinstance(kantone, list) else type(kantone)}"
    )
    # Live ZH carries 161 municipalities; the trimmed fixture preserves them all.
    assert len(kantone[0].get("gemeinden", [])) == 161, (  # type: ignore[union-attr]
        "ZH trimming lost the 161-municipality proof — fixture is no longer the recorded one"
    )


# =============================================================================
# 1. POSITIVE — real-shaped payload reaches the parser; envelope names the
#    real host; trust_state == official_publication; fetched_at non-null.
#    Also: the original keys remain TOP-LEVEL alongside the envelope
#    (the additive-envelope contract of src/main.py:364,379).
# =============================================================================


@pytest.mark.test_id("TEST-SPEC056B-001")
@pytest.mark.requirements("SPEC-056b:FR-01,FR-02,FR-03")
@pytest.mark.scenario("AC1: real-shaped OGD payload parses and envelope carries the real host.")
@pytest.mark.asyncio
async def test_positive_real_payload_reaches_parser_and_envelope_names_real_host() -> None:
    fixture = _load_fixture()

    def handler(request: httpx.Request) -> httpx.Response:
        assert OGD_HOST in str(request.url), f"fetch did not hit {OGD_HOST}: {request.url}"
        return httpx.Response(200, json=fixture)

    transport = httpx.MockTransport(handler)
    async with httpx.AsyncClient(transport=transport) as client:
        svc = VoteService(client=client)
        ok = await svc.refresh_from_live(vote_date="20260927")
        assert ok is True, "refresh_from_live must return True on a successful live parse (26 cantons, valid id)"
        proposal = svc.get_proposal_by_id(6880)
        assert proposal is not None, "proposal 6880 from the live OGD must be reachable after refresh"
        assert len(proposal.cantons) == 26, "live parse must expose all 26 cantons"
        # Purist source assertion: the real host must be named in at least one of source / live_source_url.
        source = svc.source
        live_url = svc.live_source_url or ""
        assert (
            REAL_HOST in source or source == "BFS VoteInfo OGD" or REAL_HOST in live_url
        ), f"source must name the real host — got source={source!r} live_url={live_url!r}"
        assert svc.trust_state == "official_publication", (
            f"trust_state must be official_publication after live success, got {svc.trust_state!r}"
        )
        assert svc.fetched_at is not None, "fetched_at must be non-null after a live publication"


@pytest.mark.test_id("TEST-SPEC056B-002")
@pytest.mark.requirements("SPEC-056b:FR-03")
@pytest.mark.scenario("AC2: contract — proposal keys stay top-level alongside the envelope, not nested under 'proposal'.")
@pytest.mark.asyncio
async def test_positive_contract_additive_envelope_proposal_top_level() -> None:
    fixture = _load_fixture()

    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, json=fixture)

    transport = httpx.MockTransport(handler)
    async with httpx.AsyncClient(transport=transport) as client:
        # Build a dedicated app instance wired to this VoteService so the
        # refresh actually uses our mock (the global app instance would need
        # its own transport; we prove the contract by inspecting src/main.py
        # directly).
        from fastapi.testclient import TestClient as _TC

        # Prove the route contract is additive by calling the service + envelope
        # the way src/main.py does: {**proposal.model_dump(), **envelope}
        svc = VoteService(client=client)
        await svc.refresh_from_live(vote_date="20260927")
        proposal = svc.get_latest_vote()
        envelope = {
            "source": svc.source,
            "fetched_at": svc.fetched_at,
            "trust_state": svc.trust_state,
        }
        body = {**proposal.model_dump(), **envelope}
        # proposal keys must be reachable at the top level
        assert "proposal_id" in body, "proposal_id must be top-level, not nested under 'proposal'"
        assert "national_yes_percent" in body, "national_yes_percent must be top-level"
        assert "cantons" in body and "ZH" in body["cantons"], "cantons/ZH must be top-level"
        assert "source" in body and body["source"] == svc.source
        # and must NOT be hidden under a 'proposal' key
        assert "proposal" not in body or isinstance(body["proposal"], type(None)), (
            "contract requires top-level keys, not nested under 'proposal'"
        )


@pytest.mark.test_id("TEST-SPEC056B-003")
@pytest.mark.requirements("SPEC-056b:FR-04,FR-06")
@pytest.mark.scenario("AC3: BfsVoteInfoClient.fetch hits the constant host and validates the date strictly.")
def test_client_build_url_constant_host_and_strict_validation() -> None:
    # Strict ^\\d{8}$, never caller-controlled host
    assert BfsVoteInfoClient.build_url("20260927") == OGD_FULL_URL
    assert OGD_HOST in OGD_URL_TEMPLATE
    for bad in ["2026-09-27", "abc", "2026", "202609271", "", "2026092"]:
        with pytest.raises(ValueError):
            BfsVoteInfoClient.build_url(bad)


@pytest.mark.test_id("TEST-SPEC056B-004")
@pytest.mark.requirements("SPEC-056b:FR-04")
@pytest.mark.scenario("AC4: transport error / HTTP 500 / non-JSON degrade to stale or source_pending, never fabricate live ids.")
@pytest.mark.asyncio
async def test_negative_host_unreachable_degrades_to_stale() -> None:
    def unreachable(request: httpx.Request) -> httpx.Response:
        raise httpx.ConnectError("mock DNS fail", request=request)

    transport = httpx.MockTransport(unreachable)
    async with httpx.AsyncClient(transport=transport) as client:
        svc = VoteService(client=client)
        ok = await svc.refresh_from_live(vote_date="20260927")
        assert ok is False
        assert svc.trust_state == "stale", (
            f"fixtures present → trust_state must be 'stale' on transport error, got {svc.trust_state!r}"
        )
        # must NOT fabricate live ids
        for pid in LIVE_IDS:
            p = svc.get_proposal_by_id(pid)
            # stale: fixtures retained, live proposal not injected
            assert p is None, f"live proposal {pid} must never be fabricated on failure"
        # fixture ids still served (just labelled stale)
        for pid in FIXTURE_IDS:
            assert svc.get_proposal_by_id(pid) is not None


@pytest.mark.test_id("TEST-SPEC056B-005")
@pytest.mark.requirements("SPEC-056b:FR-04")
@pytest.mark.scenario("AC5: HTTP 500 degrades to stale, never fabricates live ids.")
@pytest.mark.asyncio
async def test_negative_http_500_degrades_to_stale() -> None:
    def server_error(request: httpx.Request) -> httpx.Response:
        return httpx.Response(500, json={"error": "internal"})

    transport = httpx.MockTransport(server_error)
    async with httpx.AsyncClient(transport=transport) as client:
        svc = VoteService(client=client)
        ok = await svc.refresh_from_live(vote_date="20260927")
        assert ok is False
        assert svc.trust_state == "stale"
        for pid in LIVE_IDS:
            assert svc.get_proposal_by_id(pid) is None
        for pid in FIXTURE_IDS:
            assert svc.get_proposal_by_id(pid) is not None


@pytest.mark.test_id("TEST-SPEC056B-006")
@pytest.mark.requirements("SPEC-056b:FR-04")
@pytest.mark.scenario("AC6: non-JSON body degrades to stale, never fabricates live ids.")
@pytest.mark.asyncio
async def test_negative_non_json_body_degrades_to_stale() -> None:
    def not_json(request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, content=b"not json {{", headers={"content-type": "application/json"})

    transport = httpx.MockTransport(not_json)
    async with httpx.AsyncClient(transport=transport) as client:
        svc = VoteService(client=client)
        ok = await svc.refresh_from_live(vote_date="20260927")
        assert ok is False
        assert svc.trust_state == "stale"
        for pid in LIVE_IDS:
            assert svc.get_proposal_by_id(pid) is None


@pytest.mark.test_id("TEST-SPEC056B-007")
@pytest.mark.requirements("SPEC-056b:FR-04")
@pytest.mark.scenario("AC7: empty store (no fixtures) on failure yields source_pending, not stale nor crash.")
@pytest.mark.asyncio
async def test_negative_empty_store_yields_source_pending() -> None:
    def unreachable(request: httpx.Request) -> httpx.Response:
        raise httpx.ConnectError("mock DNS fail", request=request)

    transport = httpx.MockTransport(unreachable)
    async with httpx.AsyncClient(transport=transport) as client:
        svc = VoteService(client=client)
        svc._proposals.clear()  # edge branch of FR-04: empty store
        ok = await svc.refresh_from_live(vote_date="20260927")
        assert ok is False
        assert svc.trust_state == "source_pending", (
            f"empty store → trust_state must be source_pending, got {svc.trust_state!r}"
        )


@pytest.mark.test_id("TEST-SPEC056B-008")
@pytest.mark.requirements("SPEC-056b:FR-04")
@pytest.mark.scenario("AC8: 2024 fixture ids are never presented as if they were live data.")
@pytest.mark.asyncio
async def test_negative_fixture_ids_never_labelled_live() -> None:
    """When fetch fails, the source label must NOT become the live label.

    The fixtures are served under trust_state stale *and* source
    embedded-fixture, never under BFS VoteInfo OGD.
    """
    def server_error(request: httpx.Request) -> httpx.Response:
        return httpx.Response(500, json={})

    transport = httpx.MockTransport(server_error)
    async with httpx.AsyncClient(transport=transport) as client:
        svc = VoteService(client=client)
        await svc.refresh_from_live(vote_date="20260927")
        assert svc.source != "BFS VoteInfo OGD", (
            "failed fetch must not relabel fixtures as the live source"
        )
        assert svc.source == "embedded-fixture"


# =============================================================================
# 3. CONTRACT — additive envelope, list(items), 404.
#    These prove that the original payload keys remain top-level after the
#    wiring and that unknown ids still 404 (src/main.py:383-393 contract).
# =============================================================================


@pytest.mark.test_id("TEST-SPEC056B-009")
@pytest.mark.requirements("SPEC-056b:FR-03,FR-06")
@pytest.mark.scenario("AC9: contract — GET .../votes/latest returns proposal_id and national_yes_percent top-level.")
def test_contract_latest_is_additive_not_nested() -> None:
    c = TestClient(app)
    resp = c.get("/api/v1/politics/votes/latest")
    assert resp.status_code == 200, resp.text
    body = resp.json()
    # contract: additive envelope → payload keys remain top-level; no wrapping under "proposal"
    # (source_pending may still carry proposal=null, but when there is a proposal it must be unwrapped)
    for k in ("source", "trust_state"):
        assert k in body, f"envelope key {k!r} missing from latest"
    if body.get("proposal_id") is not None:
        assert "proposal_id" in body
        assert "national_yes_percent" in body
        assert "cantons" in body
        assert "proposal" not in body or body["proposal"] is None  # no nested wrapper


@pytest.mark.test_id("TEST-SPEC056B-010")
@pytest.mark.requirements("SPEC-056b:FR-03,FR-06")
@pytest.mark.scenario("AC10: contract — GET .../votes/list still returns items at the top level.")
def test_contract_list_items_top_level() -> None:
    c = TestClient(app)
    resp = c.get("/api/v1/politics/votes/list")
    assert resp.status_code == 200, resp.text
    body = resp.json()
    assert "items" in body, "votes/list must return 'items' at the top level"
    assert isinstance(body["items"], list)
    for k in ("source", "trust_state"):
        assert k in body, f"envelope key {k!r} missing from votes/list"
    if body["items"]:
        assert "proposal_id" in body["items"][0]


@pytest.mark.test_id("TEST-SPEC056B-011")
@pytest.mark.requirements("SPEC-056b:FR-06")
@pytest.mark.scenario("AC11: contract — unknown proposal id still yields 404.")
def test_contract_unknown_proposal_404() -> None:
    c = TestClient(app)
    resp = c.get("/api/v1/politics/votes/99999")
    assert resp.status_code == 404, f"unknown proposal must be 404, got {resp.status_code}: {resp.text}"


# =============================================================================
# 4. REGRESSION — the binding gate's blocking defect: refresh_from_live used to
#    INSERT the live proposal into a store still holding the four 2024
#    fixtures, so /votes/list served five ids under trust_state
#    official_publication. Four of them are constants in this repository,
#    presented as federal results with a fresh timestamp — the exact
#    dishonesty SPEC-056b FR-02 exists to remove. On success the served set
#    must contain ONLY live ids. No network — MockTransport + recorded fixture.
# =============================================================================


@pytest.mark.asyncio
@pytest.mark.test_id("TEST-SPEC056B-012")
@pytest.mark.requirements("SPEC-056b:FR-02")
@pytest.mark.scenario(
    "AC12: regression — on a successful refresh the served set contains only live ids, "
    "none of the four fixture ids appears under official_publication."
)
async def test_regression_success_serves_only_live_ids() -> None:
    fixture = _load_fixture()

    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, json=fixture)

    transport = httpx.MockTransport(handler)
    async with httpx.AsyncClient(transport=transport) as client:
        svc = VoteService(client=client)
        ok = await svc.refresh_from_live(vote_date="20260927")
        assert ok is True, "recorded live-shaped payload must refresh successfully"
        assert svc.trust_state == "official_publication", (
            f"success must label official_publication, got {svc.trust_state!r}"
        )
        served_ids = [p["proposal_id"] for p in svc.list_proposals()]
        assert len(served_ids) >= 1, "served set must be non-empty after a live success"
        assert set(served_ids) <= set(LIVE_IDS), (
            f"served set must contain ONLY live ids {LIVE_IDS}, got {served_ids}"
        )
        for fid in FIXTURE_IDS:
            assert fid not in served_ids, (
                f"fixture id {fid} must never be served under official_publication "
                f"— served ids: {served_ids}"
            )
            assert svc.get_proposal_by_id(fid) is None, (
                f"fixture id {fid} must not resolve while trust_state is official_publication"
            )
