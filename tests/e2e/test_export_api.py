"""SPEC-020 E2E contract — GET /api/v1/place/{postcode}/export (json|csv)."""

from fastapi.testclient import TestClient

from src.main import app

client = TestClient(app)


def test_export_e2e_json_roundtrip_8004() -> None:
    r = client.get("/api/v1/place/8004/export?format=json")
    assert r.status_code == 200
    body = r.json()
    assert body["postcode"] == "8004"
    assert body["data"]["place"]["postcode"] == "8004"
    assert all(k in body["data"] for k in ("place", "solar", "oereb", "steuerfuss", "planning"))
    assert "source_pending" in str(body["sources"]) or "official" in str(body["sources"])


def test_export_e2e_csv_8004_content_disposition_and_semicolon() -> None:
    r = client.get("/api/v1/place/8004/export?format=csv")
    assert r.status_code == 200
    assert "text/csv" in r.headers["content-type"]
    assert "attachment" in r.headers["content-disposition"]
    # Swiss ; convention
    assert "section;field;value;source;trust_state;fetched_at" in r.text
    assert "place;postcode;8004" in r.text


def test_export_e2e_format_422() -> None:
    assert client.get("/api/v1/place/8004/export?format=pdf").status_code == 422
    assert client.get("/api/v1/place/8004/export?format=Xml").status_code == 422


def test_export_e2e_unknown_plz_404() -> None:
    assert client.get("/api/v1/place/9999/export?format=json").status_code == 404
    assert client.get("/api/v1/place/9999/export?format=csv").status_code == 404
