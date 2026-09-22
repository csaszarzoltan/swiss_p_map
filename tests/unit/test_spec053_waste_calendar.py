"""SPEC-053 unit tests: relative waste schedule + real .ics export."""

from datetime import UTC, date, datetime

from src.services.municipal_service import MunicipalService


def test_spec_053_req_053_001_ac_053_001_relative_schedule() -> None:
    w = MunicipalService().waste("8004")
    assert w.events, "expected upcoming collection events"
    today = datetime.now(UTC).date()
    dates = [date.fromisoformat(e.collection_date) for e in w.events]
    assert dates == sorted(dates)
    assert all(d >= today for d in dates)
    for e in w.events:
        assert e.days_until == (date.fromisoformat(e.collection_date) - today).days


def test_spec_053_req_053_002_ac_053_001_source_trust_metadata() -> None:
    w = MunicipalService().waste("8004")
    assert w.source and w.fetched_at and w.trust_state
    assert w.trust_state != "official_measurement"


def test_spec_053_req_053_001_ac_053_001_ics_matches_events() -> None:
    svc = MunicipalService()
    w = svc.waste("8004")
    ics = svc.waste_ics("8004")
    assert ics.startswith("BEGIN:VCALENDAR")
    assert ics.strip().endswith("END:VCALENDAR")
    assert ics.count("BEGIN:VEVENT") == len(w.events)
    for e in w.events:
        assert e.collection_date.replace("-", "") in ics


def test_spec_053_req_053_001_ac_053_001_ics_api() -> None:
    from fastapi.testclient import TestClient

    from src.main import app

    r = TestClient(app).get("/api/v1/municipal/waste-calendar.ics?postcode=8004")
    assert r.status_code == 200
    assert "text/calendar" in r.headers["content-type"]
    assert r.text.count("BEGIN:VEVENT") >= 1


def test_spec_053_req_053_001_ac_053_001_waste_calendar_api_contract() -> None:
    from fastapi.testclient import TestClient

    from src.main import app

    body = TestClient(app).get("/api/v1/municipal/waste-calendar?postcode=8004").json()
    assert body["postcode"] == "8004"
    assert body["events"] and body["fetched_at"] and body["trust_state"]
    assert all("days_until" in e and "collection_date" in e for e in body["events"])
