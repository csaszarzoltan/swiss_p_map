"""Politics domain models — representatives, proposals, districts."""

from __future__ import annotations

from enum import Enum

from pydantic import BaseModel, Field


class PoliticalParty(str, Enum):
    SP = "SP"
    FDP = "FDP"
    SVP = "SVP"
    GRUENE = "Grüne"
    GLP = "GLP"
    MITTE = "Die Mitte"
    AL = "AL"
    EVP = "EVP"
    OTHER = "Other"


class ParliamentaryProposal(BaseModel):
    id: str
    title: str
    type: str = Field(description="Motion, Postulat, Interpellation, ...")
    status: str = Field(description="Eingereicht, Überwiesen, Abgeschlossen, ...")
    submitted_date: str
    topic_category: str = ""


class Representative(BaseModel):
    id: str
    name: str
    party: PoliticalParty
    wahlkreis: str
    email: str | None = None
    proposals: list[ParliamentaryProposal] = Field(default_factory=list)


class DistrictRepresentatives(BaseModel):
    """Representatives for a given Wahlkreis / postcode."""

    district_name: str
    postcode: str
    canton: str
    representatives: list[Representative]
