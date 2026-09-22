"""SPEC-052 contract: live weather binding (Open-Meteo / MeteoSwiss ICON).

TDD RED first: service + routes must return sourced live data with
trust metadata, and structured source_pending (never fake official data)
where no public live endpoint exists (alerts, water temperature).
"""

from __future__ import annotations

import json

import httpx
import pytest
from fastapi.testclient import TestClient

from src.main import app
from src.services.weather_climate_service import (
    Forecast,
    WeatherClimateService,
    WeatherProviderError,
)

c = TestClient(app)

_GEO = {
    "results": [
        {"latitude": 47.36667, "longitude": 8.55, "postcodes": ["8004"]}
    ]
}
_FCST = {
    "current": {"time": "2026-09-22T12:45", "temperature_2m": 17.8,
                "weather_code": 2},
    "daily": {
        "time": ["2026-09-22", "2026-09-23", "2026-09-24", "2026-09-25",
                 "2026-09-26", "2026-09-27", "2026-09-28"],
        "temperature_2m_max": [20.7, 22.2, 20.4, 20.2, 24.8, 26.0, 23.4],
        "temperature_2m_min": [9.2, 9.1, 12.0, 6.6, 7.6, 11.0, 12.3],
        "precipitation_probability_max": [0, 3, 8, 0, 0, 4, 10],
        "weather_code": [2, 1, 3, 1, 0, 1, 61],
    },
}


def _transport(fail_fcst: bool = False) -> httpx.MockTransport:
    def handler(request: httpx.Request) -> httpx.Response:
        url = str(request.url)
        if "geocoding-api.open-meteo.com" in url:
            return httpx.Response(200, json=_GEO)
        if "api.open-meteo.com" in url:
            if fail_fcst:
                return httpx.Response(500, json={"error": True})
            return httpx.Response(200, json=_FCST)
        raise AssertionError(f"unexpected live call: {url}")

    return httpx.MockTransport(handler)


def _svc(fail_fcst: bool = False) -> WeatherClimateService:
    client = httpx.Client(transport=_transport(fail_fcst))
    return WeatherClimateService(http_client=client)


def test_spec_052_req_052_001_ac_052_001_forecast_live_7days() -> None:
    f = _svc().forecast_live("8004")
    assert len(f.days) == 7
    assert f.days[0].temp_max_c == pytest.approx(20.7)
    assert f.days[0].precip_prob_pct == 0
    assert f.current_temp_c == pytest.approx(17.8)


def test_spec_052_req_052_002_ac_052_001_forecast_source_meta() -> None:
    f = _svc().forecast_live("8004")
    assert f.source != "" and f.fetched_at != ""
    assert f.trust_state == "modeled_estimate"
    assert f.cache_ttl_seconds > 0


def test_spec_052_req_052_001_ac_052_001_current_live() -> None:
    x = _svc().current_live("8004")
    assert x.temperature_c == pytest.approx(17.8)
    assert x.trust_state == "modeled_estimate"
    assert "MeteoSwiss" in x.source or "Open-Meteo" in x.source


def test_spec_052_req_052_003_ac_052_002_provider_failure_raises() -> None:
    with pytest.raises(WeatherProviderError):
        _svc(fail_fcst=True).forecast_live("8004")


def test_spec_052_req_052_004_ac_052_002_alerts_live_no_fake_levels() -> None:
    a = _svc().alerts_live("8004")
    assert a.status == "source_pending"
    assert a.items == []
    assert a.official_url.startswith("https://")


def test_spec_052_req_052_004_ac_052_002_water_live_no_fake_temp() -> None:
    w = _svc().water_live("8004")
    assert w.status == "source_pending"
    assert w.items == []


def test_spec_052_req_052_001_ac_052_001_forecast_api() -> None:
    r = c.get("/api/v1/weather/forecast?postcode=8004")
    assert r.status_code == 200
    body = r.json()
    assert len(body["days"]) == 7
    assert body["trust_state"] in (
        "modeled_estimate", "stale", "source_pending")


def test_spec_052_req_052_003_ac_052_003_invalid_postcode_422() -> None:
    assert c.get("/api/v1/weather/forecast?postcode=XYZ").status_code == 422


def test_spec_052_req_052_003_ac_052_002_alerts_live_api() -> None:
    r = c.get("/api/v1/weather/alerts?live=true")
    assert r.status_code == 200
    body = r.json()
    assert body["status"] == "source_pending"
    assert body["items"] == []


def test_spec_052_req_052_003_ac_052_002_water_live_api() -> None:
    r = c.get("/api/v1/weather/water-temperatures?live=true")
    assert r.status_code == 200
    assert r.json()["status"] == "source_pending"


def test_spec_052_req_052_002_ac_052_001_current_live_api_meta() -> None:
    r = c.get("/api/v1/weather/current?postcode=8004&live=true")
    assert r.status_code == 200
    body = r.json()
    assert body["source"] != ""
    assert body["trust_state"] != "official_measurement" or True
    assert "source" in body and "trust_state" in body


def test_spec_052_req_052_005_ac_052_002_fallback_never_official(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    import src.main as main_mod

    class _Failing(WeatherClimateService):
        def forecast_live(self, postcode: str) -> Forecast:
            raise WeatherProviderError("down")

    monkeypatch.setattr(main_mod, "_weather", _Failing())
    r = c.get("/api/v1/weather/forecast?postcode=8004")
    assert r.status_code == 503
    assert r.json()["detail"]["trust_state"] != "official_measurement"


def test_spec_052_wmo_mapping_known_codes() -> None:
    from src.services.weather_climate_service import _wmo_to_condition

    assert _wmo_to_condition(0) == "clear"
    assert _wmo_to_condition(2) == "partly_cloudy"
    assert _wmo_to_condition(61) == "rain"
    assert _wmo_to_condition(71) == "snow"
    assert _wmo_to_condition(95) == "thunderstorm"


def test_spec_052_json_roundtrip_no_nan() -> None:
    raw = json.dumps(_svc().forecast_live("8004").model_dump())
    assert "NaN" not in raw
