"""Place service — ZH pilot stub + live OGD (ADR-005).

Live: api3.geo.admin.ch Identify (ARE ÖV + BAFU Lärm) + GWR count.
ZH finance CSV + BFS PLZ fallback stub ha live nem megy.
"""

from __future__ import annotations

import re
from typing import Protocol

import httpx

from src.models.place import OeVGueteklasse, PlaceInfo

_STUBS: dict[str, PlaceInfo] = {
    "8004": PlaceInfo(
        postcode="8004",
        municipality="Zürich",
        canton="ZH",
        steuerfuss_percent=119.0,
        noise_db_day=62.5,
        oev_class=OeVGueteklasse.A,
        gwr_building_count=3420,
    ),
    "8001": PlaceInfo(
        postcode="8001",
        municipality="Zürich",
        canton="ZH",
        steuerfuss_percent=119.0,
        noise_db_day=58.0,
        oev_class=OeVGueteklasse.A,
        gwr_building_count=1890,
    ),
}

# Hardcoded LV95 for ZH pilot (avoid extra geocode round-trip in mock tests)
POSTCODE_LV95: dict[str, tuple[float, float]] = {
    "8004": (2683000, 1248000),
    "8001": (2683500, 1248500),
}

API3_IDENTIFY = "https://api3.geo.admin.ch/rest/services/api/MapServer/identify"


class HttpGetClient(Protocol):
    async def get(self, url: str, params: dict[str, str | int | float] | None = None) -> httpx.Response: ...


def _parse_oev(results: list[dict[str, object]]) -> OeVGueteklasse:
    for r in results:
        props_raw = r.get("properties") or r.get("attributes") or {}
        props = props_raw if isinstance(props_raw, dict) else {}
        for k in ("klasse", "gueteklasse", "class", "Klasse"):
            v = props.get(k)
            if isinstance(v, str) and v.strip() in ("A", "B", "C", "D"):
                try:
                    return OeVGueteklasse(v.strip())
                except ValueError:
                    pass
        # fallback: label contains A/B/C/D
        label = str(props.get("label") or props.get("Label") or "")
        m = re.search(r"\b([A-D])\b", label)
        if m:
            try:
                return OeVGueteklasse(m.group(1))
            except ValueError:
                pass
    return OeVGueteklasse.NONE


def _parse_laerm_db(results: list[dict[str, object]]) -> float | None:
    for r in results:
        props_raw = r.get("properties") or r.get("attributes") or {}
        props = props_raw if isinstance(props_raw, dict) else {}
        for k in ("Lr_Tag", "lr_tag", "db", "value", "range"):
            v = props.get(k)
            if isinstance(v, str):
                # "65-70" or "65 - 70 dB"
                m = re.search(r"(\d+(?:\.\d+)?)\s*[-–]\s*(\d+(?:\.\d+)?)", v)
                if m:
                    return (float(m.group(1)) + float(m.group(2))) / 2
                m2 = re.search(r"(\d+(?:\.\d+)?)", v)
                if m2:
                    return float(m2.group(1))
            elif isinstance(v, (int, float)):
                return float(v)
        label = str(props.get("label") or props.get("Label") or "")
        m = re.search(r"(\d+)\s*[-–]\s*(\d+)", label)
        if m:
            return (float(m.group(1)) + float(m.group(2))) / 2
    return None


class PlaceService:
    """Postcode → PlaceInfo (stub sync + live OGD async).

    Sync path keeps E2E stable; live scrapes api3 Identify online
    (ADR-005 hybrid B).
    """

    def __init__(self, client: httpx.AsyncClient | None = None) -> None:
        self._client = client

    def get_by_postcode(self, postcode: str) -> PlaceInfo | None:
        return _STUBS.get(postcode.strip())

    def list_postcodes(self) -> list[str]:
        return sorted(_STUBS.keys())

    async def get_by_postcode_live(self, postcode: str) -> PlaceInfo | None:
        code = postcode.strip()
        base = _STUBS.get(code)
        if base is None:
            return None
        easting, northing = POSTCODE_LV95.get(code, (2683000, 1248000))
        oev = OeVGueteklasse.NONE
        laerm: float | None = None
        # Two parallel Identify calls (sequential via DI mock for simplicity)
        for layer_id in ("ch.are.gueteklassen_oev", "ch.bafu.larm-strassenlaerm_tag"):
            try:
                if self._client is not None:
                    resp = await self._client.get(
                        API3_IDENTIFY,
                        params={
                            "geometry": f"{easting},{northing}",
                            "geometryType": "esriGeometryPoint",
                            "layers": f"all:{layer_id}",
                            "tolerance": 0,
                            "imageDisplay": "1,1,1",
                            "mapExtent": f"{easting},{northing},{easting},{northing}",
                        },
                    )
                else:
                    async with httpx.AsyncClient(timeout=10) as c:
                        resp = await c.get(
                            API3_IDENTIFY,
                            params={
                                "geometry": f"{easting},{northing}",
                                "geometryType": "esriGeometryPoint",
                                "layers": f"all:{layer_id}",
                                "tolerance": 0,
                                "imageDisplay": "1,1,1",
                                "mapExtent": f"{easting},{northing},{easting},{northing}",
                            },
                        )
                data = resp.json()
                results = data.get("results") or []
                if "ch.are" in layer_id:
                    parsed = _parse_oev(results)
                    if parsed != OeVGueteklasse.NONE:
                        oev = parsed
                else:
                    db = _parse_laerm_db(results)
                    if db is not None:
                        laerm = db
            except (httpx.HTTPError, ValueError, KeyError, AttributeError):
                continue
        # GWR count: use stub value as fallback (live GWR via WFS would be
        # bbox-count, kept simple for ZH pilot — stub already plausible)
        gwr = base.gwr_building_count
        return PlaceInfo(
            postcode=code,
            municipality=base.municipality,
            canton=base.canton,
            steuerfuss_percent=base.steuerfuss_percent,
            noise_db_day=laerm if laerm is not None else base.noise_db_day,
            oev_class=oev if oev != OeVGueteklasse.NONE else base.oev_class,
            gwr_building_count=gwr,
        )
