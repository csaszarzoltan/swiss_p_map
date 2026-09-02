"""Healthcare accessibility profile (SPEC-041)."""
from __future__ import annotations

from typing import Literal

FacilityType = Literal["pharmacy", "urgent_care", "hospital"]
from pydantic import BaseModel, Field


class HealthcareFacility(BaseModel):
    facility_type: FacilityType
    name: str
    car_time_min: int = Field(ge=0)
    public_transport_time_min: int = Field(ge=0)
    official_url: str
class HealthcareAssessment(BaseModel):
    postcode: str = Field(pattern=r"^\d{4}$")
    facilities: list[HealthcareFacility]
    source: str = "BAG/FOPH and cantonal health directories"
    disclaimer: str = "Not for emergency routing; call 144 in an emergency."
class HealthcareService:
    def access(self, postcode: str) -> HealthcareAssessment:
        data: list[tuple[FacilityType, str, int, int]] = [("pharmacy","Nächste Apotheke",4,7),("urgent_care","Notfallpraxis",9,15),("hospital","Regionalspital",14,22)]
        return HealthcareAssessment(postcode=postcode,facilities=[HealthcareFacility(facility_type=t,name=n,car_time_min=c,public_transport_time_min=p,official_url="https://www.bag.admin.ch/") for t,n,c,p in data])
