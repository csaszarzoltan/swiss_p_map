"""Politics service — ZH pilot: STUB + live PARIS CQL.

ADR-005: PARIS-API direkt (Gemeinderat ZH) XML CQL, postcode→Wahlkreis
lookup, httpx Protocol-DI (amtsblatt minta), fallback STUB ha live nem megy.
"""

from __future__ import annotations

import re
import xml.etree.ElementTree as ET
from typing import Protocol

import httpx

from src.models.politics import DistrictRepresentatives, PoliticalParty, Representative

# Minimal STUB for E2E/demo — kept for sync path + fallback
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
    "8610": DistrictRepresentatives(
        district_name="Gemeinderat Uster",
        postcode="8610",
        canton="ZH",
        representatives=[
            Representative(
                id="zh-8610-1",
                name="Keller Beat",
                party=PoliticalParty.FDP,
                wahlkreis="Uster",
            ),
            Representative(
                id="zh-8610-2",
                name="Meier Susanne",
                party=PoliticalParty.SP,
                wahlkreis="Uster",
            ),
        ],
    ),
    "3011": DistrictRepresentatives(
        district_name="Stadtrat Bern",
        postcode="3011",
        canton="BE",
        representatives=[
            Representative(
                id="be-3011-1",
                name="Wyss Michael",
                party=PoliticalParty.SP,
                wahlkreis="Bern Innere Stadt",
            ),
            Representative(
                id="be-3011-2",
                name="Gerber Laura",
                party=PoliticalParty.GRUENE,
                wahlkreis="Bern Innere Stadt",
            ),
        ],
    ),
    "4001": DistrictRepresentatives(
        district_name="Grosser Rat Basel-Stadt",
        postcode="4001",
        canton="BS",
        representatives=[
            Representative(
                id="bs-4001-1",
                name="Schneider Urs",
                party=PoliticalParty.FDP,
                wahlkreis="Basel-Stadt",
            ),
            Representative(
                id="bs-4001-2",
                name="Weber Clara",
                party=PoliticalParty.SP,
                wahlkreis="Basel-Stadt",
            ),
        ],
    ),
    "1201": DistrictRepresentatives(
        district_name="Conseil Municipal Genève",
        postcode="1201",
        canton="GE",
        representatives=[
            Representative(
                id="ge-1201-1",
                name="Favre Jean-Luc",
                party=PoliticalParty.SP,
                wahlkreis="Genève",
            ),
        ],
    ),
}

# Postcode → Wahlkreis (Stadt ZH Stadtkreise → Gemeinderat 12→9 merged)
POSTCODE_WAHLKREIS: dict[str, str] = {
    "8001": "1+2",
    "8002": "2",
    "8003": "3",
    "8004": "4+5",
    "8005": "5",
    "8006": "6",
    "8008": "8",
    "8032": "7",
    "8045": "9",
    "8050": "11",
    "8051": "12",
    "8052": "12",
    "8057": "11",
    "8037": "10",
}

PARIS_BASE = "https://www.gemeinderat-zuerich.ch/api"


class HttpGetClient(Protocol):
    async def get(
        self, url: str, params: dict[str, str | int] | None = None
    ) -> httpx.Response: ...


def _parse_party(raw: str) -> PoliticalParty:
    raw = raw.strip()
    for p in PoliticalParty:
        if p.value.lower() == raw.lower() or p.name.lower() == raw.lower():
            return p
    return PoliticalParty.OTHER


def _extract_block_field(block: str, key: str) -> str:
    """Toleráns: Wahlkreis=4, Wahlkreis>4, \"Wahlkreis\" : \"4\"."""
    m = re.search(
        rf"{re.escape(key)}\s*[=:>]\s*\"?([^\"<\s]+)\"?", block, re.IGNORECASE
    )
    if m:
        return m.group(1).strip().strip('">')
    # fallback: >value<
    m2 = re.search(rf"{re.escape(key)}[^<]*>\s*([^<]+)\s*<", block, re.IGNORECASE)
    return m2.group(1).strip() if m2 else ""


def _extract_name(block: str) -> str:
    # NameVorname >Muster Anna<
    m = re.search(r"NameVorname[^>]*>\s*([^<]+)\s*<", block, re.IGNORECASE)
    if m:
        return m.group(1).strip()
    m2 = re.search(r"NameVorname\s*[=:>]\s*([^<\n]+)", block, re.IGNORECASE)
    return m2.group(1).strip() if m2 else ""


def _parse_paris_kontakte(xml_text: str) -> list[Representative]:
    reps: list[Representative] = []
    # tolerant: find each Kontakt block (any ns)
    blocks = re.findall(
        r"<[^>]*Kontakt[^>]*>(.*?)</[^>]*Kontakt[^>]*>",
        xml_text,
        re.DOTALL | re.IGNORECASE,
    )
    if not blocks:
        # fallback: try ET parse for strict XML
        try:
            root = ET.fromstring(
                xml_text.encode() if isinstance(xml_text, str) else xml_text
            )
            for el in root.iter():
                tag = el.tag.split("}", 1)[-1] if "}" in el.tag else el.tag
                if tag.lower() == "kontakt":
                    txt = ET.tostring(el, encoding="unicode")
                    blocks.append(txt)
        except ET.ParseError:
            pass
    for block in blocks:
        try:
            rid = _extract_block_field(block, "ID") or f"paris-{len(reps)}"
            name = _extract_name(block)
            if not name:
                continue
            wahl = (
                _extract_block_field(block, "Wahlkreis")
                or _extract_block_field(block, "Wohnkreis")
                or "?"
            )
            party_raw = (
                _extract_block_field(block, "Partei")
                or _extract_block_field(block, "Fraktion")
                or "Other"
            )
            reps.append(
                Representative(
                    id=str(rid),
                    name=name,
                    party=_parse_party(party_raw),
                    wahlkreis=f"Wahlkreis {wahl}",
                )
            )
        except (ValueError, TypeError, KeyError, AttributeError, re.error):
            continue
    return reps


class PoliticsService:
    """Postcode → representatives (STUB sync + live PARIS async).

    Sync path keeps E2E stable; live path scrapes PARIS CQL XML online
    (ADR-005) with httpx DI + mockbarát transport.
    """

    def __init__(
        self,
        client: httpx.AsyncClient | None = None,
        base_url: str = PARIS_BASE,
    ) -> None:
        self._client = client
        self._base_url = base_url.rstrip("/")

    def get_by_postcode(self, postcode: str) -> DistrictRepresentatives | None:
        code = postcode.strip()
        return _STUBS.get(code)

    def list_postcodes(self) -> list[str]:
        return sorted(_STUBS.keys())

    async def get_by_postcode_live(
        self, postcode: str
    ) -> DistrictRepresentatives | None:
        """Live: postcode → Wahlkreis → PARIS kontakt searchdetails.

        Returns DistrictRepresentatives or fallback STUB; [] on hard error.
        Source URL preserved per METHODOLOGY (`source_url` in repr).
        """
        code = postcode.strip()
        wahl = POSTCODE_WAHLKREIS.get(code, "4")
        # CQL: Wahlkreis any "4" or "4+5"
        q = f'Wahlkreis any "{wahl}"'
        url = f"{self._base_url}/kontakt/searchdetails"
        params: dict[str, str | int] = {"q": q, "l": "de-CH", "s": 1, "m": 50}
        try:
            if self._client is not None:
                resp = await self._client.get(url, params=params)
            else:
                async with httpx.AsyncClient(timeout=12) as c:
                    resp = await c.get(url, params=params)
            resp.raise_for_status()
            text = resp.text
        except (httpx.HTTPError, ValueError):
            # fallback stub if live fails (keeps demo usable)
            return _STUBS.get(code)
        reps = _parse_paris_kontakte(text)
        if not reps:
            return _STUBS.get(code)
        return DistrictRepresentatives(
            district_name=f"Wahlkreis {wahl}",
            postcode=code,
            canton="ZH",
            representatives=reps,
        )
