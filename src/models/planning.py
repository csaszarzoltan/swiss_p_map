"""Planning domain model — Baugesuch with Auflage-ablak TTL."""

from __future__ import annotations

from datetime import date, timedelta

from pydantic import BaseModel, Field

AUFLAGE_DAYS: int = 20
"""Default Auflage duration (Einsprache window) — publication_date + 20 days.

The Amtsblattportal's ``expirationDate`` is a ~1 year visibility TTL,
not the legal Auflage period; this constant encodes the legal window
as a documented approximation (see ADR-002).
"""


class Baugesuch(BaseModel):
    """Baugesuch (building permit application publication).

    Mirrors Amtsblattportal ``BP-ZH01`` fields that map 1:1, plus
    derived Auflage window and geocoding.
    """

    id: str = Field(..., min_length=1)
    title: str = Field(..., min_length=1)
    municipality: str = Field(..., min_length=1)
    municipality_id: int | None = None
    postcode: str = Field(..., min_length=4, max_length=4)
    canton: str = Field(default="ZH", min_length=2, max_length=2)
    publication_date: date
    expiration_date: date
    auflage_start: date | None = None
    auflage_end: date | None = None
    source_url: str = Field(..., min_length=1)
    geocode_precision: str = Field(default="none")
    lat: float | None = None
    lon: float | None = None
    contractor: str | None = None
    architect: str | None = None
    parcel_number: str | None = None
    zone_type: str | None = None
    risk_level: str | None = None

    def model_post_init(self, __context: object, /) -> None:
        if self.auflage_start is None:
            object.__setattr__(self, "auflage_start", self.publication_date)
        if self.auflage_end is None:
            object.__setattr__(
                self,
                "auflage_end",
                self.publication_date + timedelta(days=AUFLAGE_DAYS),
            )
        if self.risk_level is None:
            # Rule-based automatic risk scoring (ADR-016)
            title_lower = self.title.lower()
            if (
                "aufstockung" in title_lower
                or "kernzone" in title_lower
                or "abbruch" in title_lower
            ):
                object.__setattr__(self, "risk_level", "high")
            elif "neubau" in title_lower or "gewerbe" in title_lower:
                object.__setattr__(self, "risk_level", "medium")
            else:
                object.__setattr__(self, "risk_level", "low")

    def is_active(self, on: date) -> bool:
        """True if on is within the Auflage (Einsprache) window (inclusive)."""
        assert self.auflage_start is not None and self.auflage_end is not None
        return self.auflage_start <= on <= self.auflage_end
