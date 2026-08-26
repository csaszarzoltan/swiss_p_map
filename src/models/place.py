"""Place domain models — Steuerfuss / sonBASE / ÖV-Güteklassen.

Mocks provide deterministic OGD-like fixtures for tests and local dev
until real ingesters are wired (ADR-001 Phase 1 / Phase 2).
"""

from __future__ import annotations

from enum import Enum
from typing import Annotated

from pydantic import BaseModel, ConfigDict, Field

# Reuse WGS84 bounds from geo so both domains share one truth.
from src.models.geo import WGS84_LAT_MAX, WGS84_LAT_MIN, WGS84_LON_MAX, WGS84_LON_MIN

# --- Canton allowlist (26 Swiss cantons) ---------------------------------
VALID_CANTONS: frozenset[str] = frozenset(
    {
        "AG",
        "AI",
        "AR",
        "BE",
        "BL",
        "BS",
        "FR",
        "GE",
        "GL",
        "GR",
        "JU",
        "LU",
        "NE",
        "NW",
        "OW",
        "SG",
        "SH",
        "SO",
        "SZ",
        "TG",
        "TI",
        "UR",
        "VD",
        "VS",
        "ZG",
        "ZH",
    }
)


# --- Steuerfuss ------------------------------------------------------------


class SteuerfussEntry(BaseModel):
    """Gemeindesteuerfuss (municipal tax multiplier) per BFS & year."""

    model_config = ConfigDict(frozen=True, strict=True)

    municipality: Annotated[str, Field(min_length=1)]
    bfs_number: Annotated[int, Field(ge=1, le=9999)]
    canton: Annotated[str, Field(min_length=2, max_length=2, pattern=r"^[A-Z]{2}$")]
    year: Annotated[int, Field(ge=2000, le=2035)]
    steuerfuss_percent: Annotated[float, Field(ge=0, le=500)]

    def model_post_init(self, _context: object) -> None:
        if self.canton not in VALID_CANTONS:
            raise ValueError(f"Unknown canton code: {self.canton}")


def mock_steuerfuss_entries() -> list[SteuerfussEntry]:
    """Deterministic fixtures — Zürich + Winterthur 2024."""
    return [
        SteuerfussEntry(
            municipality="Zürich",
            bfs_number=261,
            canton="ZH",
            year=2024,
            steuerfuss_percent=119.0,
        ),
        SteuerfussEntry(
            municipality="Winterthur",
            bfs_number=230,
            canton="ZH",
            year=2024,
            steuerfuss_percent=122.0,
        ),
    ]


# --- sonBASE (noise) -------------------------------------------------------


class NoiseSource(str, Enum):
    """Noise exposure source — sonBASE layers."""

    ROAD = "road"
    RAIL = "rail"
    AIR = "air"


class SonBaseExposure(BaseModel):
    """Point noise exposure (Lr dB) from sonBASE / Lärmkarte."""

    model_config = ConfigDict(frozen=True, strict=True)

    latitude: Annotated[float, Field(ge=WGS84_LAT_MIN, le=WGS84_LAT_MAX)]
    longitude: Annotated[float, Field(ge=WGS84_LON_MIN, le=WGS84_LON_MAX)]
    db_day: Annotated[float, Field(ge=0, le=120)]
    db_night: Annotated[float, Field(ge=0, le=120)]
    source: NoiseSource


def mock_sonbase_entries() -> list[SonBaseExposure]:
    """Single fixture — road noise at Zürich HB."""
    return [
        SonBaseExposure(
            latitude=47.3781,
            longitude=8.5401,
            db_day=65.0,
            db_night=55.0,
            source=NoiseSource.ROAD,
        ),
    ]


# --- ÖV-Güteklassen --------------------------------------------------------


class OeVGueteklasse(str, Enum):
    """ÖV-Güteklasse — federal public-transport quality classes (ARE)."""

    A = "A"
    B = "B"
    C = "C"
    D = "D"
    NONE = "NONE"


class OeVGueteklasseEntry(BaseModel):
    """ÖV-Güteklassen point rating (ARE/BAV)."""

    model_config = ConfigDict(frozen=True, strict=True)

    latitude: Annotated[float, Field(ge=WGS84_LAT_MIN, le=WGS84_LAT_MAX)]
    longitude: Annotated[float, Field(ge=WGS84_LON_MIN, le=WGS84_LON_MAX)]
    guteklasse: OeVGueteklasse
    stop_name: str | None = None


def mock_oev_gueteklasse_entries() -> list[OeVGueteklasseEntry]:
    """Single fixture — Güteklasse A at Zürich HB."""
    return [
        OeVGueteklasseEntry(
            latitude=47.3781,
            longitude=8.5401,
            guteklasse=OeVGueteklasse.A,
            stop_name="Zürich HB",
        ),
    ]
