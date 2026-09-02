"""SPEC-050 municipal services."""

from pydantic import BaseModel, Field


class Waste(BaseModel):
    postcode: str = Field(pattern=r"^\d{4}$")
    events: list[dict[str, str]]
    source: str = "Municipal waste calendar"


class WaterQuality(BaseModel):
    postcode: str = Field(pattern=r"^\d{4}$")
    hardness_fh: float
    hardness_dh: float
    classification: str
    source: str = "Municipal water utility"


class MunicipalService:
    def waste(self, p: str) -> Waste:
        return Waste(
            postcode=p,
            events=[
                {"waste_type": "Papier", "collection_date": "2026-09-08"},
                {"waste_type": "Karton", "collection_date": "2026-09-15"},
            ],
        )

    def water(self, p: str) -> WaterQuality:
        return WaterQuality(
            postcode=p, hardness_fh=28, hardness_dh=15.7, classification="hart"
        )
