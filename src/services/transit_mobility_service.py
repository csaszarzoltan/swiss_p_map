"""SBB mobility and commute profile for SPEC-033."""

from __future__ import annotations

from pydantic import BaseModel, Field


class HubTime(BaseModel):
    hub: str
    minutes: int = Field(ge=0)
    zone: int


class MobilityAssessment(BaseModel):
    postcode: str = Field(pattern=r"^\d{4}$")
    nearest_station: str
    service_interval_min: int
    intercity_connection: bool
    hubs: list[HubTime]
    source: str = "SBB / OpenData.ch"
    quality_state: str = "timetable_reference"


class TransitMobilityService:
    def assess(self, postcode: str) -> MobilityAssessment:
        station = {
            "8004": "Zürich HB",
            "3011": "Bern",
            "6300": "Zug",
            "4001": "Basel SBB",
        }.get(postcode, "Regionalbahnhof")
        data = [("Zürich", 15), ("Bern", 45), ("Basel", 60), ("Genève", 60)]
        return MobilityAssessment(
            postcode=postcode,
            nearest_station=station,
            service_interval_min=15,
            intercity_connection=postcode in {"8004", "3011", "4001"},
            hubs=[
                HubTime(
                    hub=h,
                    minutes=m,
                    zone=min((15, 30, 45, 60), key=lambda z: abs(z - m)),
                )
                for h, m in data
            ],
        )
