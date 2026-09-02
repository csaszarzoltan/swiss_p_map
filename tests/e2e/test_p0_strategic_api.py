"""HTTP acceptance paths with REQ/AC traceability for P0 strategic features."""

from fastapi.testclient import TestClient

from src.main import app

client = TestClient(app)


def test_spec_034_req_001_ac_001_prices_endpoint() -> None:
    response = client.get("/api/v1/property/prices?canton=ZH&postcode=8004")
    assert response.status_code == 200
    body = response.json()
    assert len(body["segments"]) == 2
    assert body["quality_state"] == "official_regional_estimate"


def test_spec_032_req_002_ac_002_tax_endpoint() -> None:
    response = client.get("/api/v1/tax/comparison?canton=ZG")
    assert response.status_code == 200
    assert response.json()["selected"]["national_rank"] == 1


def test_spec_035_req_003_ac_005_hazard_validation() -> None:
    assert (
        client.get("/api/v1/hazard/assessment?postcode=8004&lat=90&lon=8.5").status_code
        == 422
    )
    body = client.get(
        "/api/v1/hazard/assessment?postcode=8004&lat=47.37&lon=8.52"
    ).json()
    assert body["quality_state"] == "indicative_model"


def test_spec_036_req_001_ac_001_isos_endpoint() -> None:
    body = client.get("/api/v1/heritage/isos?postcode=3011").json()
    assert body["protected"] is True
    assert body["classification"] == "ISOS I"
