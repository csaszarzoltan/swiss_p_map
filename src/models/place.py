"""Place domain models — Steuerfuss, noise, ÖV-Güteklassen, GWR."""

from __future__ import annotations

from enum import Enum

from pydantic import BaseModel, Field


class OeVGueteklasse(str, Enum):
    """ÖV-Güteklassen per ARE (A=best, none=not classified)."""

    A = "A"
    B = "B"
    C = "C"
    D = "D"
    NONE = "none"


class PlaceInfo(BaseModel):
    """Aggregated place/property data for a postcode/municipality."""

    postcode: str = Field(..., description="Swiss postcode (4 digits)")
    municipality: str
    canton: str
    steuerfuss_percent: float | None = Field(None, ge=0, description="Gemeindesteuerfuss in %")
    noise_db_day: float | None = Field(None, description="sonBASE day noise dB(A)")
    oev_class: OeVGueteklasse = OeVGueteklasse.NONE
    gwr_building_count: int | None = Field(None, ge=0)
