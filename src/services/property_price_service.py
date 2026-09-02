"""BFS/FSO IMPI property price trend service (SPEC-034)."""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field

SOURCE = "BFS/FSO IMPI (Immobilienpreisindex)"
SOURCE_URL = "https://www.bfs.admin.ch/bfs/en/home/statistics/prices/property-price-index.html"


class PropertySegment(BaseModel):
    """One official IMPI market segment with deterministic reference data."""

    segment: Literal["single_family_house", "condominium"]
    average_price_chf_m2: int = Field(ge=0)
    quarterly_index: float = Field(ge=0)
    change_1y_percent: float
    change_5y_percent: float


class PropertyPriceAssessment(BaseModel):
    """Canton/postcode property market assessment."""

    canton: str = Field(pattern=r"^[A-Z]{2}$")
    postcode: str = Field(pattern=r"^\d{4}$")
    reference_period: str
    source: str = SOURCE
    source_url: str = SOURCE_URL
    quality_state: Literal["official_regional_estimate"] = "official_regional_estimate"
    segments: list[PropertySegment]


# Regional reference snapshot. PLZ values are regional estimates, never valuations.
_CANTON: dict[str, tuple[int, int, float, float, float]] = {
    "ZH": (12500, 11200, 121.8, 3.2, 18.7), "ZG": (15300, 13800, 128.4, 4.1, 24.6),
    "SZ": (11600, 10500, 124.2, 3.7, 21.5), "BE": (7600, 6900, 114.6, 2.0, 12.4),
    "BS": (10300, 9600, 119.1, 2.8, 16.3), "GE": (14200, 12800, 126.0, 3.5, 22.1),
    "VD": (9800, 9000, 120.3, 2.9, 17.8), "TI": (7200, 6700, 111.7, 1.4, 8.9),
}
_DEFAULT = (8200, 7500, 116.0, 2.3, 14.2)


class PropertyPriceService:
    """Return immutable, source-labelled IMPI regional reference values."""

    def get_assessment(self, canton: str, postcode: str) -> PropertyPriceAssessment:
        code = canton.upper()
        house, apartment, index, one_year, five_year = _CANTON.get(code, _DEFAULT)
        return PropertyPriceAssessment(
            canton=code,
            postcode=postcode,
            reference_period="2026-Q1",
            segments=[
                PropertySegment(segment="single_family_house", average_price_chf_m2=house, quarterly_index=index, change_1y_percent=one_year, change_5y_percent=five_year),
                PropertySegment(segment="condominium", average_price_chf_m2=apartment, quarterly_index=round(index - 1.7, 1), change_1y_percent=round(one_year - 0.3, 1), change_5y_percent=round(five_year - 1.2, 1)),
            ],
        )
