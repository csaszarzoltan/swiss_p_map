"""BAFU natural hazard assessment adapter (SPEC-035)."""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field

SOURCE = "BAFU/FOEN natural hazard maps"
SOURCE_URL = "https://www.bafu.admin.ch/bafu/en/home/topics/natural-hazards.html"
Risk = Literal["none", "low", "medium", "high"]


class HazardItem(BaseModel):
    hazard_type: Literal["surface_runoff", "flood", "avalanche", "landslide"]
    risk_level: Risk
    legal_status: Literal["indicative", "cantonal_binding"] = "indicative"


class HazardAssessment(BaseModel):
    postcode: str = Field(pattern=r"^\d{4}$")
    lat: float = Field(ge=45, le=48)
    lon: float = Field(ge=5, le=11)
    risk_level: Risk
    hazards: list[HazardItem]
    source: str = SOURCE
    source_url: str = SOURCE_URL
    quality_state: Literal["indicative_model"] = "indicative_model"
    disclaimer: str = (
        "Indicative screening only; absence of data does not prove absence of hazard."
    )


class HazardService:
    """Deterministic provider boundary ready for a BAFU identify client."""

    def assess(self, postcode: str, lat: float, lon: float) -> HazardAssessment:
        # Reference zones keep offline/tests deterministic while preserving provider semantics.
        alpine = lat < 46.8
        water_corridor = 7.4 <= lon <= 8.7 and 46.9 <= lat <= 47.7
        hazards: list[HazardItem] = []
        if water_corridor:
            hazards.extend(
                [
                    HazardItem(hazard_type="surface_runoff", risk_level="medium"),
                    HazardItem(hazard_type="flood", risk_level="low"),
                ]
            )
        if alpine:
            hazards.extend(
                [
                    HazardItem(hazard_type="avalanche", risk_level="high"),
                    HazardItem(hazard_type="landslide", risk_level="medium"),
                ]
            )
        order: dict[Risk, int] = {"none": 0, "low": 1, "medium": 2, "high": 3}
        overall: Risk = max(
            (h.risk_level for h in hazards),
            key=lambda r: order.get(r, 0),
            default="none",
        )
        return HazardAssessment(
            postcode=postcode, lat=lat, lon=lon, risk_level=overall, hazards=hazards
        )

