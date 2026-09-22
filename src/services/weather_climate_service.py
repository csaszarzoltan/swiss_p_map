"""SPEC-052 weather service — live Open-Meteo (MeteoSwiss ICON) + stubs.

Design:
- Sync stub path (current/alerts/water) kept for existing SPEC-048 tests.
- NEW live path: postcode -> open-meteo geocoding -> forecast API
  (models=icon_seamless, MeteoSwiss ICON CH for Switzerland).
- No public live JSON for official MeteoSwiss danger levels or BAFU
  lake temperatures -> alerts_live / water_live return structured
  source_pending (never fabricated official values, REQ-052-004/005).
"""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Any, Literal

import httpx
from pydantic import BaseModel, Field

_GEO_URL = "https://geocoding-api.open-meteo.com/v1/search"
_FCST_URL = "https://api.open-meteo.com/v1/forecast"
_TIMEOUT_S = 10.0
_CACHE_TTL_S = 900

TrustState = Literal[
    "official_measurement",
    "official_publication",
    "modeled_estimate",
    "stale",
    "source_pending",
]


class WeatherProviderError(RuntimeError):
    """Raised when the live weather provider is unreachable/invalid."""


def _wmo_to_condition(code: int) -> str:
    if code == 0:
        return "clear"
    if code in (1,):
        return "mostly_clear"
    if code in (2,):
        return "partly_cloudy"
    if code in (3,):
        return "overcast"
    if code in (45, 48):
        return "fog"
    if code in (51, 53, 55, 56, 57):
        return "drizzle"
    if code in (61, 63, 65, 66, 67, 80, 81, 82):
        return "rain"
    if code in (71, 73, 75, 77, 85, 86):
        return "snow"
    if code in (95, 96, 99):
        return "thunderstorm"
    return "unknown"


class Current(BaseModel):
    postcode: str = Field(pattern=r"^\d{4}$")
    temperature_c: float
    condition: str
    observed_at: str
    source: str = "MeteoSwiss"
    trust_state: str = "official_measurement"


class Alert(BaseModel):
    region: str
    level: int = Field(ge=1, le=5)
    event: str
    valid_until: str
    source: str = "MeteoSwiss"


class Water(BaseModel):
    water_body: str
    temperature_c: float
    observed_at: str
    source: str


class ForecastDay(BaseModel):
    date: str
    temp_min_c: float
    temp_max_c: float
    precip_prob_pct: int = Field(ge=0, le=100)
    condition: str


class Forecast(BaseModel):
    postcode: str = Field(pattern=r"^\d{4}$")
    current_temp_c: float
    current_condition: str
    observed_at: str
    days: list[ForecastDay]
    source: str = "Open-Meteo / MeteoSwiss ICON"
    trust_state: TrustState = "modeled_estimate"
    fetched_at: str
    cache_ttl_seconds: int = _CACHE_TTL_S


class LiveCurrent(BaseModel):
    postcode: str = Field(pattern=r"^\d{4}$")
    temperature_c: float
    condition: str
    observed_at: str
    source: str = "Open-Meteo / MeteoSwiss ICON"
    trust_state: TrustState = "modeled_estimate"
    fetched_at: str
    cache_ttl_seconds: int = _CACHE_TTL_S


class LiveList(BaseModel):
    status: TrustState = "source_pending"
    items: list[dict[str, Any]] = Field(default_factory=list)
    source: str
    official_url: str
    fetched_at: str
    note: str = ""


class WeatherClimateService:
    """Weather service with stub sync path + live Open-Meteo binding."""

    def __init__(self, http_client: httpx.Client | None = None) -> None:
        self._http = http_client

    def _client(self) -> httpx.Client:
        if self._http is not None:
            return self._http
        return httpx.Client(timeout=_TIMEOUT_S)

    # ---- legacy stub path (SPEC-048 compat) ----
    def current(self, p: str) -> Current:
        return Current(
            postcode=p,
            temperature_c=21.5,
            condition="partly_cloudy",
            observed_at="2026-09-02T12:00:00Z",
        )

    def alerts(self) -> list[Alert]:
        return [
            Alert(
                region="Zürich",
                level=2,
                event="Gewitter",
                valid_until="2026-09-02T18:00:00Z",
            )
        ]

    def water(self) -> list[Water]:
        return [
            Water(
                water_body="Zürichsee",
                temperature_c=22.4,
                observed_at="2026-09-02T10:00:00Z",
                source="Kanton Zürich",
            ),
            Water(
                water_body="Aare",
                temperature_c=18.7,
                observed_at="2026-09-02T10:00:00Z",
                source="BAFU",
            ),
        ]

    # ---- NEW live path (SPEC-052) ----
    def _geocode(self, postcode: str) -> tuple[float, float]:
        try:
            r = self._client().get(
                _GEO_URL,
                params={"name": postcode, "country": "Switzerland",
                        "count": 5, "format": "json"},
                timeout=_TIMEOUT_S,
            )
            r.raise_for_status()
            results = r.json().get("results") or []
        except (httpx.HTTPError, ValueError) as e:
            raise WeatherProviderError(f"geocoding failed: {e}") from e
        for row in results:
            codes = [str(x) for x in (row.get("postcodes") or [])]
            if postcode in codes:
                return float(row["latitude"]), float(row["longitude"])
        if results:
            return float(results[0]["latitude"]), float(results[0]["longitude"])
        raise WeatherProviderError(f"postcode not found: {postcode}")

    def _fetch_forecast(self, lat: float, lon: float) -> dict[str, Any]:
        try:
            r = self._client().get(
                _FCST_URL,
                params={
                    "latitude": lat,
                    "longitude": lon,
                    "models": "icon_seamless",
                    "current": "temperature_2m,weather_code",
                    "daily": ("temperature_2m_max,temperature_2m_min,"
                              "precipitation_probability_max,weather_code"),
                    "timezone": "Europe/Zurich",
                    "forecast_days": 7,
                },
                timeout=_TIMEOUT_S,
            )
            r.raise_for_status()
            body: dict[str, Any] = r.json()
        except (httpx.HTTPError, ValueError) as e:
            raise WeatherProviderError(f"forecast failed: {e}") from e
        if "daily" not in body or "current" not in body:
            raise WeatherProviderError("forecast payload incomplete")
        return body

    def forecast_live(self, postcode: str) -> Forecast:
        lat, lon = self._geocode(postcode)
        body = self._fetch_forecast(lat, lon)
        cur = body["current"]
        daily = body["daily"]
        times: list[str] = daily["time"]
        days = [
            ForecastDay(
                date=times[i],
                temp_min_c=float(daily["temperature_2m_min"][i]),
                temp_max_c=float(daily["temperature_2m_max"][i]),
                precip_prob_pct=int(
                    daily["precipitation_probability_max"][i] or 0),
                condition=_wmo_to_condition(int(daily["weather_code"][i])),
            )
            for i in range(min(7, len(times)))
        ]
        if not days:
            raise WeatherProviderError("forecast payload empty")
        now = datetime.now(UTC).isoformat()
        return Forecast(
            postcode=postcode,
            current_temp_c=float(cur["temperature_2m"]),
            current_condition=_wmo_to_condition(int(cur["weather_code"])),
            observed_at=str(cur.get("time", now)),
            days=days,
            fetched_at=now,
        )

    def current_live(self, postcode: str) -> LiveCurrent:
        f = self.forecast_live(postcode)
        return LiveCurrent(
            postcode=postcode,
            temperature_c=f.current_temp_c,
            condition=f.current_condition,
            observed_at=f.observed_at,
            fetched_at=f.fetched_at,
        )

    def alerts_live(self, postcode: str) -> LiveList:
        """No public live JSON for MeteoSwiss danger levels -> pending."""
        _ = postcode
        return LiveList(
            source="MeteoSwiss Naturgefahren",
            official_url="https://www.meteoschweiz.admin.ch/warnungen",
            fetched_at=datetime.now(UTC).isoformat(),
            note=("Keine öffentliche Live-JSON-Schnittstelle; "
                  "offizielle Warnkarte verlinkt."),
        )

    def water_live(self, postcode: str) -> LiveList:
        """BAFU lake temperature has no stable public JSON -> pending."""
        _ = postcode
        return LiveList(
            source="BAFU Hydrodaten / Eawag Alplakes",
            official_url="https://www.hydrodaten.admin.ch",
            fetched_at=datetime.now(UTC).isoformat(),
            note=("Keine stabile öffentliche Live-JSON-Schnittstelle für "
                  "See-Temperaturen; offizielle Hydrodaten verlinkt."),
        )
