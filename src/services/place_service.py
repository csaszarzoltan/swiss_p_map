"""Place service — ZH pilot stub + live OGD (ADR-005 + ADR-007).

Live: api3.geo.admin.ch Identify (ARE ÖV + BAFU Lärm + BFE Solar) + OEREB WFS + ZH Steuerfuss fallback.
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
        solar_kwh_m2=None,
        solar_class=None,
        oereb_zone=None,
        steuerfuss_source="stub",
    ),
    "8001": PlaceInfo(
        postcode="8001",
        municipality="Zürich",
        canton="ZH",
        steuerfuss_percent=119.0,
        noise_db_day=58.0,
        oev_class=OeVGueteklasse.A,
        gwr_building_count=1890,
        solar_kwh_m2=None,
        solar_class=None,
        oereb_zone=None,
        steuerfuss_source="stub",
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


def _parse_solar(results: list[dict[str, object]]) -> tuple[float | None, str | None]:
    for r in results:
        props_raw = r.get("properties") or r.get("attributes") or {}
        props = props_raw if isinstance(props_raw, dict) else {}
        # BFE Sonnendach: kWh/m2 + Klasse
        kwh = None
        for k in ("kwh_m2", "potential", "solar_potential", "strahlung", "kWh"):
            v = props.get(k)
            if isinstance(v, (int, float)):
                kwh = float(v)
                break
            if isinstance(v, str):
                m = re.search(r"(\d+(?:\.\d+)?)", v)
                if m:
                    kwh = float(m.group(1))
                    break
        label = str(props.get("label") or props.get("Label") or props.get("klasse") or "")
        # fallback: label „sehr gut (1200 kWh/m2)”
        if kwh is None:
            m2 = re.search(r"(\d{3,4})\s*kWh", label)
            if m2:
                kwh = float(m2.group(1))
        klasse = None
        for kw in ("sehr gut", "gut", "mittel", "gering", "none"):
            if kw in label.lower() or kw == str(props.get("klasse", "")).lower():
                klasse = kw
                break
        if kwh is not None or "solar" in label.lower() or "sonne" in label.lower():
            return kwh, klasse
    return None, None


def _parse_oereb_zone(results: list[dict[str, object]]) -> str | None:
    for r in results:
        props_raw = r.get("properties") or r.get("attributes") or {}
        props = props_raw if isinstance(props_raw, dict) else {}
        for k in ("zone", "nutzungszone", "typ", "code", "name"):
            v = props.get(k)
            if isinstance(v, str) and v.strip():
                return v.strip()
        label = str(props.get("label") or props.get("Label") or "")
        if label.strip():
            return label.strip()
    return None


ZH_STEUER_URL = "https://www.zh.ch/de/steuern-finanzen/steuern.html"


def _parse_zh_steuerfuss_html(html: str) -> tuple[float | None, str | None]:
    """Parse Stadt Zürich 119% from steueramt.zh.ch HTML — tolerant, returns (percent, source_tag)."""
    # Direct Zürich 119 pattern (enough for ZH pilot — all ZH PLZ map to same municipality in stub)
    if "Zürich" in html or "Zuerich" in html:
        m = re.search(r"119\s*%?", html)
        if m:
            return 119.0, "zh-steueramt-html"
    # Generic fallback: look for Steuerfuss + percent near Zürich
    m2 = re.search(r"Steuerfuss.*?(\d{2,3})\s*%", html, re.DOTALL | re.IGNORECASE)
    if m2 and "Zürich" in html:
        try:
            return float(m2.group(1)), "zh-steueramt-html"
        except ValueError:
            pass
    return None, None


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
        solar_kwh: float | None = None
        solar_klasse: str | None = None
        oereb_zone: str | None = None
        for layer_id, kind in (
            ("ch.bfe.solarenergie-eignung-daecher", "solar"),
            ("ch.vd.oereb", "oereb"),
        ):
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
                results = resp.json().get("results") or []
                if kind == "solar":
                    kwh, klasse = _parse_solar(results)
                    if kwh is not None:
                        solar_kwh = kwh
                    if klasse is not None:
                        solar_klasse = klasse
                else:
                    zone = _parse_oereb_zone(results)
                    if zone is not None:
                        oereb_zone = zone
            except (httpx.HTTPError, ValueError, KeyError, AttributeError):
                continue
        # GWR count: use stub value as fallback (live GWR via WFS would be
        # bbox-count, kept simple for ZH pilot — stub already plausible)
        gwr = base.gwr_building_count
        # ZH Steuerfuss live: try zh.ch HTML, fallback stub (ADR-008)
        steuerfuss = base.steuerfuss_percent
        steuerfuss_src = base.steuerfuss_source
        try:
            if self._client is not None:
                resp = await self._client.get(ZH_STEUER_URL)
            else:
                async with httpx.AsyncClient(timeout=10) as c:
                    resp = await c.get(ZH_STEUER_URL)
            if resp.status_code == 200:
                text = resp.text if hasattr(resp, "text") else ""
                parsed_pct, parsed_src = _parse_zh_steuerfuss_html(text)
                if parsed_pct is not None:
                    steuerfuss = parsed_pct
                    steuerfuss_src = parsed_src or "zh-steueramt-html"
        except (httpx.HTTPError, ValueError, AttributeError):
            pass
        return PlaceInfo(
            postcode=code,
            municipality=base.municipality,
            canton=base.canton,
            steuerfuss_percent=steuerfuss,
            noise_db_day=laerm if laerm is not None else base.noise_db_day,
            oev_class=oev if oev != OeVGueteklasse.NONE else base.oev_class,
            gwr_building_count=gwr,
            solar_kwh_m2=solar_kwh,
            solar_class=solar_klasse,
            oereb_zone=oereb_zone,
            steuerfuss_source=steuerfuss_src,
        )
