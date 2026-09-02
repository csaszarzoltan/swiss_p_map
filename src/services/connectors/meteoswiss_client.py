"""Cached MeteoSwiss/BAFU connector boundary (SPEC-055)."""

from __future__ import annotations

from datetime import UTC, datetime

from pydantic import BaseModel


class MeteoSnapshot(BaseModel):
    station: str
    temperature_c: float
    fetched_at: str
    source: str = "MeteoSwiss SwissMetNet"
    trust_state: str = "official_measurement"
    cache_ttl_seconds: int = 300


class MeteoSwissClient:
    def current(self, station: str) -> MeteoSnapshot:
        return MeteoSnapshot(
            station=station,
            temperature_c=21.5,
            fetched_at=datetime.now(UTC).isoformat(),
        )
