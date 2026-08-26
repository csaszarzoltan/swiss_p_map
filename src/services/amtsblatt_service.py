"""Amtsblattportal XML client — DI-friendly, httpx-injected.

Wraps https://amtsblattportal.ch/api/v1/publications/xml
Research: docs/research/2026-08-26-amtsblatt-oereb-api.md (total=6669, ~17/nap,
XML-only, nincs koordináta). ADR-002 accepted — napi poll.
"""

from __future__ import annotations

import re
import xml.etree.ElementTree as ET
from datetime import date
from typing import Protocol

import httpx

from src.models.planning import Baugesuch

AMTSBLATT_XML_URL = "https://amtsblattportal.ch/api/v1/publications/xml"


class HttpGetClient(Protocol):
    async def get(self, url: str, params: dict[str, str | int | None] | None = None) -> httpx.Response: ...


def _text(el: ET.Element | None) -> str:
    return (el.text or "").strip() if el is not None and el.text else ""


def _find_any(parent: ET.Element, local: str) -> ET.Element | None:
    """Version-tolerant: match by local name ignoring namespace (1.24 vs 1.26 drift)."""
    if parent.tag.endswith(f"}}{local}") or parent.tag == local:
        return parent
    for child in parent.iter():
        tag = child.tag
        name = tag.split("}", 1)[1] if "}" in tag else tag
        if name == local:
            return child
    return None


def _find_child_any(parent: ET.Element, local: str) -> ET.Element | None:
    for child in list(parent):
        tag = child.tag
        name = tag.split("}", 1)[1] if "}" in tag else tag
        if name == local:
            return child
    # fallback: deep search first occurrence
    return _find_any(parent, local)


def _parse_date(s: str) -> date | None:
    s = s.strip()[:10]
    try:
        return date.fromisoformat(s)
    except ValueError:
        return None


def _parse_publications(xml_text: str) -> list[Baugesuch]:
    try:
        root = ET.fromstring(xml_text)
    except ET.ParseError:
        return []
    out: list[Baugesuch] = []
    # iterate <publication> elements (any namespace)
    for pub in root.iter():
        tag = pub.tag
        name = tag.split("}", 1)[1] if "}" in tag else tag
        if name != "publication":
            continue
        try:
            pid = _text(_find_child_any(pub, "id"))
            if not pid:
                continue
            title_el = _find_child_any(pub, "title")
            title = ""
            if title_el is not None:
                de = _find_child_any(title_el, "de")
                title = _text(de) if de is not None else _text(title_el)
            if not title:
                continue
            reg = _find_child_any(pub, "registrationOffice")
            postcode = _text(_find_child_any(reg, "swissZipCode")) if reg is not None else ""
            town = _text(_find_child_any(reg, "town")) if reg is not None else ""
            muni_id_raw = _text(_find_child_any(reg, "municipalityId")) if reg is not None else ""
            municipality_id: int | None
            try:
                municipality_id = int(muni_id_raw) if muni_id_raw else None
            except ValueError:
                municipality_id = None
            if not postcode or not town:
                continue
            pub_date_raw = _text(_find_child_any(pub, "publicationDate"))
            exp_date_raw = _text(_find_child_any(pub, "expirationDate"))
            pub_date = _parse_date(pub_date_raw)
            exp_date = _parse_date(exp_date_raw)
            if pub_date is None or exp_date is None:
                continue
            cantons_el = _find_child_any(pub, "cantons")
            canton = "ZH"
            if cantons_el is not None:
                c = _find_child_any(cantons_el, "canton")
                if c is not None and _text(c):
                    canton = _text(c)[:2].upper()
            # postcode: keep 4 digits
            postcode = re.sub(r"\D", "", postcode)[:4].zfill(4) if postcode else ""
            if len(postcode) != 4:
                continue
            b = Baugesuch(
                id=pid,
                title=title,
                municipality=town,
                municipality_id=municipality_id,
                postcode=postcode,
                canton=canton,
                publication_date=pub_date,
                expiration_date=exp_date,
                source_url=f"https://amtsblattportal.ch/api/v1/publications/{pid}/xml",
            )
            out.append(b)
        except (ValueError, TypeError, KeyError, AttributeError):
            continue
    return out


class AmtsblattService:
    """Amtsblattportal XML fetcher.

    Args:
        client: httpx AsyncClient (injected — allows mocking). If None, creates one per call.
        base_url: override for tests.
    """

    def __init__(
        self,
        client: httpx.AsyncClient | None = None,
        base_url: str = AMTSBLATT_XML_URL,
    ) -> None:
        self._client = client
        self._base_url = base_url

    async def fetch_publications(
        self,
        canton: str = "ZH",
        since: date | None = None,
        rubric: str = "BP-ZH",
    ) -> list[Baugesuch]:
        """Fetch Baugesuch publications (XML bulk) — returns [] on error/empty."""
        params: dict[str, str] = {
            "publicationStates": "PUBLISHED",
            "cantons": canton,
            "rubrics": rubric,
            "pageRequest.size": str(100),
        }
        if since is not None:
            params["publicationDate.start"] = since.isoformat()
        try:
            if self._client is not None:
                resp = await self._client.get(self._base_url, params=params)
            else:
                async with httpx.AsyncClient(timeout=15) as c:
                    resp = await c.get(self._base_url, params=params)
            resp.raise_for_status()
            text = resp.text
        except (httpx.HTTPError, ValueError):
            return []
        return _parse_publications(text)
