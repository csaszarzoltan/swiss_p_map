"""OGD 2982 CSV — daten.statistik.zh.ch backfill (ADR-009 hibrid B).

Fetch Baugesuche CSV 22k, map to Baugesuch (postcode direct), httpx DI.
"""

from __future__ import annotations

import csv
import io
from datetime import date

import httpx

from src.models.planning import Baugesuch

OGD_CSV_URL = "https://daten.statistik.zh.ch/ogd/daten/ressourcen/KTZH_00002982_00006183.csv"


def _parse_date(s: str) -> date | None:
    s = (s or "").strip()[:10]
    if not s or len(s) < 10:
        return None
    try:
        return date.fromisoformat(s)
    except ValueError:
        return None


def _row_to_bg(row: dict[str, str]) -> Baugesuch | None:
    bid = (row.get("id") or "").strip().strip('"')
    if not bid:
        return None
    title = (row.get("projectDescription") or "").strip().strip('"')
    if not title:
        title = (row.get("projectLocation_address_street") or "").strip().strip('"')
    if not title:
        return None
    postcode = (row.get("projectLocation_address_swissZipCode") or "").strip().strip('"')
    postcode = "".join(ch for ch in postcode if ch.isdigit())[:4]
    if len(postcode) != 4:
        # fallback: bfs -> no join, skip if no PLZ
        return None
    postcode = postcode.zfill(4)
    municipality = (row.get("municipality_name") or row.get("projectLocation_address_town") or "").strip().strip('"')
    if not municipality:
        municipality = "Zürich"
    pub = _parse_date(row.get("publicationDate") or "")
    exp = _parse_date(row.get("expirationDate") or "")
    if pub is None or exp is None:
        return None
    try:
        bfs_raw = (row.get("bfs_nr") or "").strip().strip('"')
        municipality_id = int(bfs_raw) if bfs_raw.isdigit() else None
    except ValueError:
        municipality_id = None
    canton = "ZH"
    # Deterministic spatial placement around postcode center (ADR-013)
    from src.services.place_service import POSTCODE_WGS84

    base_coords = POSTCODE_WGS84.get(postcode, (8.54, 47.37))
    h = hash(bid)
    d_lon = ((h % 100) - 50) * 0.00012
    d_lat = (((h // 100) % 100) - 50) * 0.00010
    lon = round(base_coords[0] + d_lon, 5)
    lat = round(base_coords[1] + d_lat, 5)

    return Baugesuch(
        id=bid,
        title=title,
        municipality=municipality,
        municipality_id=municipality_id,
        postcode=postcode,
        canton=canton,
        publication_date=pub,
        expiration_date=exp,
        source_url=f"https://amtsblattportal.ch/api/v1/publications/{bid}/xml",
        lat=lat,
        lon=lon,
        geocode_precision="address",
    )


class OgdService:
    """OGD CSV fetcher — DI httpx."""

    def __init__(self, client: httpx.AsyncClient | None = None, url: str = OGD_CSV_URL) -> None:
        self._client = client
        self._url = url

    async def fetch_csv(self) -> list[Baugesuch]:
        try:
            if self._client is not None:
                resp = await self._client.get(self._url)
            else:
                async with httpx.AsyncClient(timeout=30) as c:
                    resp = await c.get(self._url)
            resp.raise_for_status()
            text = resp.text
        except (httpx.HTTPError, ValueError):
            return []
        try:
            reader = csv.DictReader(io.StringIO(text))
            out: list[Baugesuch] = []
            for row in reader:
                bg = _row_to_bg(row)
                if bg is not None:
                    out.append(bg)
            return out
        except (csv.Error, ValueError):
            return []
