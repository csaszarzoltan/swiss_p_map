"""SPEC-020 — Export audit-csomag (place+solar+oereb+steuerfuss+planning + provenance)."""

from fastapi.testclient import TestClient

from src.main import app
from src.services.export_service import ExportService

client = TestClient(app)


def test_export_service_json_shape() -> None:
    svc = ExportService()
    payload = svc.build("8004")
    assert payload is not None
    assert payload["postcode"] == "8004"
    assert "fetched_at" in payload
    assert len(payload["sources"]) == 5
    assert all("source" in s and "fetched_at" in s and "trust_state" in s for s in payload["sources"])
    data = payload["data"]
    assert "place" in data and "solar" in data and "oereb" in data and "steuerfuss" in data and "planning" in data
    assert data["planning"]["count"] >= 1  # 8004 has 2 demo baugesuche
    assert "source_pending" not in [s["trust_state"] for s in payload["sources"] if s["id"] == "planning"]


def test_export_service_csv_semicolon_separator() -> None:
    import csv
    import io
    svc = ExportService()
    csv_text = svc.to_csv("8004")
    assert csv_text is not None
    lines = csv_text.strip().split("\n")
    assert lines[0].startswith("section;field;value;source;trust_state;fetched_at")
    reader = csv.reader(io.StringIO(csv_text), delimiter=";")
    header = next(reader)
    assert header == ["section", "field", "value", "source", "trust_state", "fetched_at"]
    for row in reader:
        assert len(row) == 6, f"expected 6 columns, got {len(row)}: {row[:2]}"
    assert "place;postcode;8004" in csv_text
    assert "planning;count;" in csv_text


def test_export_service_unknown_postcode_returns_none() -> None:
    svc = ExportService()
    assert svc.build("9999") is None
    assert svc.to_json("9999") is None
    assert svc.to_csv("9999") is None


def test_export_api_json_contract() -> None:
    r = client.get("/api/v1/place/8004/export?format=json")
    assert r.status_code == 200
    assert "application/json" in r.headers["content-type"]
    assert "attachment" in r.headers["content-disposition"]
    assert 'filename="swiss-p-map-8004.json"' in r.headers["content-disposition"]
    body = r.json()
    assert body["postcode"] == "8004"
    assert body["data"]["place"]["municipality"] == "Z\u00fcrich"
    assert len(body["sources"]) == 5


def test_export_api_csv_contract_and_headers() -> None:
    r = client.get("/api/v1/place/8004/export?format=csv")
    assert r.status_code == 200
    assert "text/csv" in r.headers["content-type"]
    assert "attachment" in r.headers["content-disposition"]
    assert 'filename="swiss-p-map-8004.csv"' in r.headers["content-disposition"]
    assert r.text.startswith("section;field;value;source;trust_state;fetched_at")
    # trust_state provenance present
    assert "trust_state" in r.text


def test_export_api_invalid_format_422() -> None:
    assert client.get("/api/v1/place/8004/export?format=xml").status_code == 422
    assert client.get("/api/v1/place/8004/export?format=pdf").status_code == 422


def test_export_api_unknown_postcode_404() -> None:
    assert client.get("/api/v1/place/9999/export?format=json").status_code == 404
    assert client.get("/api/v1/place/9999/export?format=csv").status_code == 404


def test_export_api_default_format_is_json() -> None:
    r = client.get("/api/v1/place/8004/export")
    assert r.status_code == 200
    assert "application/json" in r.headers["content-type"]
