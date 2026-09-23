"""SPEC-045 traceability: resident-first local information hub contract.

RVAD traceability matrix (docs/specs/SPEC-045-...):
- REQ-045-001 -> AC-045-001 -> unit + API + E2E.
- REQ-045-002 -> AC-045-001 -> contract + SourceTrustBadge.
- REQ-045-003 -> AC-045-001..003 -> UI state E2E.
- REQ-045-004 -> AC-045-002 -> negative source-integrity test.
- REQ-045-005 -> AC-045-002 -> state recovery.
- REQ-045-006 -> AC-045-002 -> concurrency test (last-request-wins:
  responses are request-scoped; the client keeps only the latest).
"""

from fastapi.testclient import TestClient

from src.main import app
from src.services.local_information_service import LocalInformationService

client = TestClient(app)


def test_spec_045_req_045_001_ac_045_001_briefing_separates_six_resident_topics() -> None:
    result = LocalInformationService().briefing("8004")
    assert len(result.items) == 6
    assert {item.category for item in result.items} == {
        "democracy",
        "environment",
        "weather",
        "housing",
        "mobility",
        "planning",
    }
    assert all(item.source and item.source_url for item in result.items)


def test_spec_045_req_045_002_ac_045_001_every_claim_carries_source_timestamp_trust() -> None:
    result = LocalInformationService().briefing("8004")
    assert result.generated_at != ""
    for item in result.items:
        assert item.source != ""
        assert item.source_url.startswith("https://")
        assert item.status in ("current_data", "source_pending")


def test_spec_045_req_045_004_ac_045_002_pending_live_source_not_presented_as_current_news() -> None:
    weather = next(
        x
        for x in LocalInformationService().briefing("8004").items
        if x.category == "weather"
    )
    assert weather.status == "source_pending"


def test_spec_045_req_045_006_ac_045_002_responses_are_request_scoped_no_crosstalk() -> None:
    first = LocalInformationService().briefing("8004")
    second = LocalInformationService().briefing("3011")
    assert first.postcode == "8004"
    assert second.postcode == "3011"
    assert first.locality != second.locality


def test_spec_045_req_045_001_ac_045_001_api_contract_source_labelled() -> None:
    response = client.get("/api/v1/local/briefing?postcode=8004")
    assert response.status_code == 200
    body = response.json()
    assert body["postcode"] == "8004"
    assert len(body["items"]) == 6
    for item in body["items"]:
        assert item["source"]
        assert item["source_url"].startswith("https://")
        assert item["status"] in ("current_data", "source_pending")


def test_spec_045_req_045_003_ac_045_003_invalid_postcode_rejected() -> None:
    assert client.get("/api/v1/local/briefing?postcode=XYZ").status_code == 422
    assert client.get("/api/v1/local/briefing?postcode=80").status_code == 422
