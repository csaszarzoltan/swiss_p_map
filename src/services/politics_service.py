"""Politics service — Zürich pilot stub.

Resolves postcode → Wahlkreis and returns representative stubs.
PARIS-API integration point: replace _STUB_DATA with httpx fetch.
"""

from __future__ import annotations

from src.models.politics import DistrictRepresentatives, PoliticalParty, Representative

# Minimal stub data for Zürich pilot — enough for E2E / demo
_STUBS: dict[str, DistrictRepresentatives] = {
    "8004": DistrictRepresentatives(
        district_name="Wahlkreis 4+5",
        postcode="8004",
        canton="ZH",
        representatives=[
            Representative(
                id="zh-8004-1",
                name="Muster Anna",
                party=PoliticalParty.SP,
                wahlkreis="Wahlkreis 4+5",
                email="anna.muster@example.zh.ch",
            ),
            Representative(
                id="zh-8004-2",
                name="Beispiel Hans",
                party=PoliticalParty.FDP,
                wahlkreis="Wahlkreis 4+5",
                email="hans.beispiel@example.zh.ch",
            ),
        ],
    ),
    "8001": DistrictRepresentatives(
        district_name="Wahlkreis 1+2",
        postcode="8001",
        canton="ZH",
        representatives=[
            Representative(
                id="zh-8001-1",
                name="Demo Eva",
                party=PoliticalParty.GRUENE,
                wahlkreis="Wahlkreis 1+2",
            ),
        ],
    ),
}


class PoliticsService:
    """Postcode → representatives lookup (stub, PARIS-API ready)."""

    def get_by_postcode(self, postcode: str) -> DistrictRepresentatives | None:
        """Return representatives for postcode, or None if unknown."""
        # normalize: keep 4 digits
        code = postcode.strip()
        return _STUBS.get(code)

    def list_postcodes(self) -> list[str]:
        return sorted(_STUBS.keys())
