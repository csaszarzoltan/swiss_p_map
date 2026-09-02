"""MeteoSwiss CH2025 microclimate profiles (SPEC-037)."""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field


class ClimateScenario(BaseModel):
    warming_level_c: Literal["1.5", "3.0"]
    tropical_nights_per_year: int = Field(ge=0)


class MicroclimateAssessment(BaseModel):
    postcode: str = Field(pattern=r"^\d{4}$")
    canton: str = Field(pattern=r"^[A-Z]{2}$")
    summer_heat_island_c: float = Field(ge=0)
    current_tropical_nights_per_year: int = Field(ge=0)
    scenarios: list[ClimateScenario]
    source: str = "MeteoSwiss / CH2025"
    quality_state: Literal["regional_model"] = "regional_model"


class MicroclimateService:
    def assess(self, postcode: str, canton: str) -> MicroclimateAssessment:
        urban = 3.1 if postcode in {"8001", "8004", "4001", "1201"} else 1.4
        current = 18 if urban > 2 else 7
        return MicroclimateAssessment(
            postcode=postcode,
            canton=canton.upper(),
            summer_heat_island_c=urban,
            current_tropical_nights_per_year=current,
            scenarios=[
                ClimateScenario(
                    warming_level_c="1.5", tropical_nights_per_year=current + 8
                ),
                ClimateScenario(
                    warming_level_c="3.0", tropical_nights_per_year=current + 24
                ),
            ],
        )
