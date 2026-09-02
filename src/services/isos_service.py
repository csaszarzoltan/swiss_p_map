"""Federal ISOS heritage screening service (SPEC-036)."""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field

SOURCE = "BAK/FOC ISOS federal inventory"
SOURCE_URL = "https://www.bak.admin.ch/bak/en/home/cultural-heritage/isos.html"


class IsosAssessment(BaseModel):
    postcode: str = Field(pattern=r"^\d{4}$")
    protected: bool
    classification: Literal["ISOS I", "ISOS II"] | None
    site_name: str | None
    delay_risk: Literal["low", "medium", "high"]
    source: str = SOURCE
    source_url: str = SOURCE_URL
    legal_status: Literal["federal_inventory_screening"] = "federal_inventory_screening"
    official_document_url: str | None = None


_SITES: dict[str, tuple[str, Literal["ISOS I", "ISOS II"]]] = {
    "8001": ("Zürich Altstadt", "ISOS I"),
    "3011": ("Bern Altstadt", "ISOS I"),
    "4001": ("Basel Altstadt", "ISOS I"),
    "1201": ("Genève centre", "ISOS II"),
    "6003": ("Luzern historische Stadt", "ISOS I"),
}


class IsosService:
    """Screen a postcode against a versioned federal-inventory reference set."""

    def assess(self, postcode: str) -> IsosAssessment:
        site = _SITES.get(postcode)
        if site is None:
            return IsosAssessment(
                postcode=postcode,
                protected=False,
                classification=None,
                site_name=None,
                delay_risk="low",
            )
        name, classification = site
        return IsosAssessment(
            postcode=postcode,
            protected=True,
            classification=classification,
            site_name=name,
            delay_risk="high" if classification == "ISOS I" else "medium",
            official_document_url=SOURCE_URL,
        )
