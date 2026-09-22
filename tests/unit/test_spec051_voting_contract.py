"""SPEC-051 contract: GET /api/v1/votes/proposals + /{id}/analysis shape."""

from fastapi.testclient import TestClient

from src.main import app

c = TestClient(app)


def test_spec_051_req_051_001_ac_051_001_proposals_list() -> None:
    r = c.get("/api/v1/votes/proposals")
    assert r.status_code == 200
    items = r.json()["items"]
    assert len(items) >= 1
    first = items[0]
    for key in ("id", "title", "vote_date", "status", "source"):
        assert key in first, f"missing {key}"
    assert first["source"] != ""


def test_spec_051_req_051_002_ac_051_001_analysis_has_source_meta() -> None:
    proposals = c.get("/api/v1/votes/proposals").json()["items"]
    pid = proposals[0]["id"]
    r = c.get(f"/api/v1/votes/proposals/{pid}/analysis")
    assert r.status_code == 200
    body = r.json()
    assert body["proposal"]["id"] == pid
    assert isinstance(body["pro_arguments"], list)
    assert isinstance(body["contra_arguments"], list)
    assert isinstance(body["polls"], list)
    assert body["proposal"]["source"] != ""


def test_spec_051_req_051_003_ac_051_003_unknown_proposal_404() -> None:
    assert c.get("/api/v1/votes/proposals/999999/analysis").status_code == 404
