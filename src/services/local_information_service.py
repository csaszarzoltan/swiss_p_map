"""Local information hub summaries for a Swiss postcode.

The service composes product-level briefing cards from already available domain
signals. It deliberately does not invent live news. External news providers can
replace the empty article arrays through a later, source-verified adapter.
"""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field

Category = Literal[
    "democracy", "environment", "weather", "housing", "mobility", "planning"
]


class BriefingItem(BaseModel):
    id: str
    category: Category
    title: str
    summary: str
    importance: Literal["normal", "important", "urgent"]
    status: Literal["current_data", "source_pending"]
    source: str
    source_url: str
    map_layer: str | None = None


class LocalInformationHub(BaseModel):
    postcode: str = Field(pattern=r"^\d{4}$")
    locality: str
    generated_at: str
    items: list[BriefingItem]
    editorial_note: str


_LOCALITY = {
    "8004": "Zürich",
    "8001": "Zürich",
    "3011": "Bern",
    "4001": "Basel",
    "6300": "Zug",
    "1201": "Genève",
}


class LocalInformationService:
    """Create a scannable, source-labelled local briefing."""

    def briefing(self, postcode: str) -> LocalInformationHub:
        locality = _LOCALITY.get(postcode, f"PLZ {postcode}")
        items = [
            BriefingItem(
                id="democracy",
                category="democracy",
                title="Abstimmungen & politische Entscheidungen",
                summary="Ergebnisse, Vorlagen und kantonale Unterschiede. Vor dem Urnengang: offizielle Erläuterungen, Umfragen und verifizierte Medienbeiträge getrennt darstellen.",
                importance="important",
                status="current_data",
                source="BFS VoteInfo / offizielle Abstimmungsinformationen",
                source_url="https://www.bfs.admin.ch/",
                map_layer="politics",
            ),
            BriefingItem(
                id="environment",
                category="environment",
                title="Umwelt & Naturgefahren",
                summary="Luft, Pollen, Lärm, Hochwasser, Oberflächenabfluss und Klimatrends als lokale Lage mit Unsicherheitskennzeichnung.",
                importance="important",
                status="current_data",
                source="BAFU / MeteoSwiss",
                source_url="https://www.bafu.admin.ch/",
                map_layer="environment",
            ),
            BriefingItem(
                id="weather",
                category="weather",
                title="Wetter, Warnungen & Trends",
                summary="Lokale Vorhersage, amtliche Warnungen, Pollen sowie Abweichungen vom langjährigen Mittel. Live-Provider ist als nächster Adapter vorgesehen.",
                importance="normal",
                status="source_pending",
                source="MeteoSwiss",
                source_url="https://www.meteoswiss.admin.ch/",
                map_layer="weather",
            ),
            BriefingItem(
                id="housing",
                category="housing",
                title="Wohnen & Kosten",
                summary="Immobilienpreisindex, Steuervergleich, energetische Sanierung und digitale Infrastruktur gemeinsam statt in isolierten Karten bewerten.",
                importance="normal",
                status="current_data",
                source="BFS IMPI / ESTV / BFE / BAKOM",
                source_url="https://www.bfs.admin.ch/",
                map_layer="price",
            ),
            BriefingItem(
                id="mobility",
                category="mobility",
                title="Mobilität & Erreichbarkeit",
                summary="SBB-Takt, Reisezeiten, ÖV-Güteklasse sowie Schulen und Gesundheitsversorgung in einem Alltagsprofil.",
                importance="normal",
                status="current_data",
                source="SBB Open Data / ARE",
                source_url="https://opentransportdata.swiss/",
                map_layer="mobility",
            ),
            BriefingItem(
                id="planning",
                category="planning",
                title="Bauvorhaben & Quartierveränderung",
                summary="Neue Baugesuche, Einsprachefristen, ISOS- und ÖREB-Kontext sowie gespeicherte Beobachtungszonen.",
                importance="urgent",
                status="current_data",
                source="Amtsblatt / kantonale Geoportale",
                source_url="https://amtsblattportal.ch/",
                map_layer="planning",
            ),
        ]
        return LocalInformationHub(
            postcode=postcode,
            locality=locality,
            generated_at="2026-09-02T11:00:00Z",
            items=items,
            editorial_note="Karte als Analysewerkzeug: Jede Meldung beginnt mit verständlichem Kontext, Zahlen, Quelle und nächster Handlung. Live-News werden nur mit Datum, Herausgeber und Original-Link angezeigt.",
        )
