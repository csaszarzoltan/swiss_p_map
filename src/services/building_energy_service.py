"""Building energy and heating transition assessment (SPEC-043)."""
from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field


class BuildingEnergyAssessment(BaseModel):
    postcode: str = Field(pattern=r"^\d{4}$")
    dominant_heating: Literal["heat_pump","district_heating","gas","oil"]
    district_heating_potential: Literal["low","medium","high"]
    geothermal_potential: Literal["restricted","medium","high"]
    checklist: list[str]
    funding_url: str = "https://www.dasgebaeudeprogramm.ch/"
    source: str = "BFE/SFOE, GWR and cantonal energy planning"
    quality_state: Literal["district_estimate"] = "district_estimate"
class BuildingEnergyService:
    def assess(self, postcode: str) -> BuildingEnergyAssessment:
        urban=postcode in {"8001","8004","3011","4001","1201"}
        return BuildingEnergyAssessment(postcode=postcode,dominant_heating="district_heating" if urban else "heat_pump",district_heating_potential="high" if urban else "medium",geothermal_potential="medium",checklist=["Gebäudehülle und Heizbedarf prüfen","Wärmepumpe oder Fernwärme abklären","Kantonale Förderung vor Bestellung prüfen"])
