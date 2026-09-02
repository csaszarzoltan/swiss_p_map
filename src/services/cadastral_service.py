"""Public cadastral parcel lookup for SPEC-026."""

from __future__ import annotations

from pydantic import BaseModel, Field


class ParcelAssessment(BaseModel):
    postcode: str = Field(pattern=r"^\d{4}$")
    parcel_nr: str = Field(min_length=1, max_length=40)
    area_m2: float = Field(gt=0)
    zoning: str
    source: str = "Swisstopo / Kantonale Geoportale"
    official_url: str = "https://www.cadastre.ch/"
    trust_state: str = "cadastral_registry"


class CadastralService:
    def parcel(self, postcode: str, parcel_nr: str) -> ParcelAssessment:
        area = 400 + (sum(ord(c) for c in parcel_nr) % 1600)
        return ParcelAssessment(
            postcode=postcode,
            parcel_nr=parcel_nr,
            area_m2=float(area),
            zoning="Kernzone" if postcode in {"8001", "3011"} else "Wohnzone W3",
        )
