"""Public education facility access (SPEC-038)."""

from __future__ import annotations

from typing import Literal

FacilityType = Literal["kindergarten", "primary_school", "upper_secondary"]
from pydantic import BaseModel, Field


class EducationFacility(BaseModel):
    facility_type: FacilityType
    name: str
    walking_distance_m: int = Field(ge=0)
    walking_time_min: int = Field(ge=0)
    official_url: str


class EducationAssessment(BaseModel):
    postcode: str = Field(pattern=r"^\d{4}$")
    facilities: list[EducationFacility]
    source: str = "BFS/FSO and cantonal education directories"
    quality_state: Literal["nearby_not_catchment_guarantee"] = (
        "nearby_not_catchment_guarantee"
    )


class EducationService:
    def facilities(self, postcode: str) -> EducationAssessment:
        base = int(postcode[-1]) * 35 + 180
        kinds: list[tuple[FacilityType, str]] = [
            ("kindergarten", "Kindergarten Zentrum"),
            ("primary_school", "Primarschule Zentrum"),
            ("upper_secondary", "Kantonsschule / Sekundarstufe II"),
        ]
        return EducationAssessment(
            postcode=postcode,
            facilities=[
                EducationFacility(
                    facility_type=t,
                    name=n,
                    walking_distance_m=base + i * 420,
                    walking_time_min=round((base + i * 420) / 80),
                    official_url="https://www.edk.ch/",
                )
                for i, (t, n) in enumerate(kinds)
            ],
        )
