from fastapi.testclient import TestClient

from src.main import app

client = TestClient(app)


def test_local_briefing_endpoint_is_source_labelled() -> None:
    response = client.get("/api/v1/local/briefing?postcode=8004")
    assert response.status_code == 200
    assert all(item["source"] for item in response.json()["items"])
