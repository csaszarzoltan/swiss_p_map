"""Unit tests for BFS Federal Vote Service (ADR-012)."""

from fastapi.testclient import TestClient

from src.main import app
from src.services.vote_service import BFS_CANTON_MAP, VoteService


class TestVoteService:
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

    def test_vote_proposals_list_and_detail(self) -> None:
        """A /api/v1/politics/votes/list és /{id} végpontok több referendumot szolgáltatnak (ADR-017)."""
        client = TestClient(app)
        resp = client.get("/api/v1/politics/votes/list")
        assert resp.status_code == 200
        items = resp.json().get("items", [])
        assert len(items) >= 4
        ids = [p["proposal_id"] for p in items]
        assert 6670 in ids  # AHV
        assert 6680 in ids  # BVG
        assert 6690 in ids  # Autobahn
        assert 6700 in ids  # Strom

        # Detail lookup for BVG
        bvg_resp = client.get("/api/v1/politics/votes/6680")
        assert bvg_resp.status_code == 200
        bvg_data = bvg_resp.json()
        assert bvg_data["national_yes_percent"] == 32.9
        assert "ZH" in bvg_data["cantons"]
        assert bvg_data["cantons"]["ZH"]["yes_percent"] == 34.8

        # 404 for unknown proposal
        err_resp = client.get("/api/v1/politics/votes/99999")
        assert err_resp.status_code == 404
