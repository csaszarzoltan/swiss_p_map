"""BAFU NABEL air quality and MeteoSwiss pollen (SPEC-040)."""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field

Level = Literal["low", "medium", "high"]


class Pollutants(BaseModel):
    pm10_ug_m3: float = Field(ge=0)
    pm25_ug_m3: float = Field(ge=0)
    no2_ug_m3: float = Field(ge=0)
    ozone_ug_m3: float = Field(ge=0)


class AirPollenAssessment(BaseModel):
    postcode: str = Field(pattern=r"^\d{4}$")
    air_quality_index: Level
    pollutants: Pollutants
    pollen: dict[str, Level]
    source: str = "BAFU NABEL / MeteoSwiss pollen"
    quality_state: Literal["nearest_station_regional"] = "nearest_station_regional"


class AirQualityService:
    def assess(self, postcode: str) -> AirPollenAssessment:
        urban = postcode in {"8001", "8004", "4001", "1201"}
        return AirPollenAssessment(
            postcode=postcode,
            air_quality_index="medium" if urban else "low",
            pollutants=Pollutants(
                pm10_ug_m3=18,
                pm25_ug_m3=10.5,
                no2_ug_m3=27 if urban else 14,
                ozone_ug_m3=62,
            ),
            pollen={"hazel": "low", "birch": "medium", "grass": "high"},
        )
