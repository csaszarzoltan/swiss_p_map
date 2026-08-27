"""Place service — ZH pilot stub + live OGD (ADR-005 + ADR-007).

Live: api3.geo.admin.ch Identify (ARE ÖV + BAFU Lärm + BFE Solar) + OEREB WFS + ZH Steuerfuss fallback.
"""

from __future__ import annotations

import re
from typing import Protocol

import httpx

from src.models.place import OeVGueteklasse, PlaceInfo


def _mk_stub(
    pc: str, muni: str, canton: str, steuer: float, noise: float, oev: OeVGueteklasse, gwr: int
) -> PlaceInfo:
    return PlaceInfo(
        postcode=pc,
        municipality=muni,
        canton=canton,
        steuerfuss_percent=steuer,
        noise_db_day=noise,
        oev_class=oev,
        gwr_building_count=gwr,
        solar_kwh_m2=None,
        solar_class=None,
        oereb_zone=None,
        steuerfuss_source="stub",
    )


_STUBS: dict[str, PlaceInfo] = {
    "8004": _mk_stub("8004", "Zürich", "ZH", 119.0, 62.5, OeVGueteklasse.A, 3420),
    "8001": _mk_stub("8001", "Zürich", "ZH", 119.0, 58.0, OeVGueteklasse.A, 1890),
    "8610": _mk_stub("8610", "Uster", "ZH", 110.0, 55.0, OeVGueteklasse.B, 4200),
    "3011": _mk_stub("3011", "Bern", "BE", 154.0, 59.0, OeVGueteklasse.A, 2900),
    "4001": _mk_stub("4001", "Basel", "BS", 130.0, 60.0, OeVGueteklasse.A, 3100),
    "1201": _mk_stub("1201", "Genève", "GE", 145.0, 61.0, OeVGueteklasse.A, 2600),
}

# LV95 coordinates for pilot and quick-pick regions
POSTCODE_LV95: dict[str, tuple[float, float]] = {
    "8004": (2683000, 1248000),
    "8001": (2683500, 1248500),
    "8610": (2697014, 1245446),
    "3011": (2600709, 1199563),
    "4001": (2611267, 1267359),
    "1201": (2500294, 1118466),
}

# WGS84 building polygon centers (BFE solar is building-polygon)
POSTCODE_WGS84: dict[str, tuple[float, float]] = {
    "8004": (8.534, 47.378),
    "8001": (8.540, 47.377),
    "8610": (8.723, 47.353),
    "3011": (7.448, 46.947),
    "4001": (7.588, 47.557),
    "1201": (6.147, 46.210),
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
    klasse_map = {1: "gering", 2: "mittel", 3: "gut", 4: "sehr gut"}
    for r in results:
        props_raw = r.get("properties") or r.get("attributes") or {}
        props = props_raw if isinstance(props_raw, dict) else {}
        # BFE Sonnendach: mstrahlung (=kWh/m2) or stromertrag/flaeche derived
        kwh = None
        for k in ("mstrahlung", "kwh_m2", "potential", "solar_potential", "strahlung", "kWh"):
            v = props.get(k)
            if isinstance(v, (int, float)):
                kwh = float(v)
                break
            if isinstance(v, str):
                m = re.search(r"(\d+(?:\.\d+)?)", v)
                if m:
                    kwh = float(m.group(1))
                    break
        # Derived: stromertrag / flaeche ≈ kWh/m2 * yield
        if kwh is None:
            strom = props.get("stromertrag")
            flaeche = props.get("flaeche")
            if isinstance(strom, (int, float)) and isinstance(flaeche, (int, float)) and flaeche > 1:
                kwh = round(float(strom) / float(flaeche) * 8.0, 1)  # ~ yield scaler; fallback to mstrahlung if present
                # Prefer mstrahlung if both exist
                if isinstance(props.get("mstrahlung"), (int, float)):
                    kwh = float(props["mstrahlung"])
        if kwh is None:
            fl = props.get("flaeche_kollektoren")
            strom2 = props.get("waermeertrag")
            if isinstance(fl, (int, float)) and fl > 1 and isinstance(strom2, (int, float)):
                kwh = round(float(strom2) / float(fl) * 2.5, 1)
        label = str(props.get("label") or props.get("Label") or props.get("klasse") or "")
        # fallback: label „sehr gut (1200 kWh/m2)”
        if kwh is None:
            m2 = re.search(r"(\d{3,4})\s*kWh", label)
            if m2:
                kwh = float(m2.group(1))
        klasse = None
        raw_klasse = props.get("klasse")
        if isinstance(raw_klasse, int) and raw_klasse in klasse_map:
            klasse = klasse_map[raw_klasse]
        elif isinstance(raw_klasse, str) and raw_klasse.strip().isdigit():
            try:
                klasse = klasse_map[int(raw_klasse.strip())]
            except KeyError:
                pass
        if klasse is None:
            for kw in ("sehr gut", "gut", "mittel", "gering", "none"):
                if kw in label.lower() or kw == str(props.get("klasse", "")).lower():
                    klasse = kw
                    break
        # If we have mstrahlung/klasse from BFE, return even without label solar
        has_signal = kwh is not None or klasse is not None or isinstance(props.get("mstrahlung"), (int, float))
        if has_signal or "solar" in label.lower() or "sonne" in label.lower():
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


def _parse_oereb_xml(xml_text: str) -> str | None:
    """Parse ZH WFS Nutzungsplanung XML → typ_gde_bezeichnung (Kernzone, Wohnzone etc)."""
    import xml.etree.ElementTree as ET

    try:
        root = ET.fromstring(xml_text)
    except ET.ParseError:
        return None
    # Namespace-agnostic search for typ_gde_bezeichnung
    for el in root.iter():
        tag = el.tag.split("}", 1)[-1] if "}" in el.tag else el.tag
        if tag == "typ_gde_bezeichnung" and el.text and el.text.strip():
            return el.text.strip()
    for el in root.iter():
        tag = el.tag.split("}", 1)[-1] if "}" in el.tag else el.tag
        if tag == "typ_zh_bezeichnung" and el.text and el.text.strip():
            return el.text.strip()
    return None


ZH_WFS_URL = "https://maps.zh.ch/wfs/OerebKatasterZHWFS"


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
    (ADR-005 + ADR-011 multi-canton expansion).
    """

    def __init__(self, client: httpx.AsyncClient | None = None) -> None:
        self._client = client

    def get_by_postcode(self, postcode: str) -> PlaceInfo | None:
        stub = _STUBS.get(postcode.strip())
        if stub is None:
            return None
        lvl, reason = self._risk_for(stub, stub.steuerfuss_percent, stub.noise_db_day, stub.solar_kwh_m2, stub.oereb_zone)
        if stub.risk_level is not None:
            return stub
        return stub.model_copy(update={"risk_level": lvl, "risk_reason": reason})

    def list_postcodes(self) -> list[str]:
        return sorted(_STUBS.keys())

    async def _safe_get(
        self, url: str, params: dict[str, str | int | float] | None = None
    ) -> httpx.Response | None:
        try:
            if self._client is not None:
                return await self._client.get(url, params=params)
            async with httpx.AsyncClient(timeout=10) as c:
                return await c.get(url, params=params)
        except (httpx.HTTPError, ValueError, AttributeError, KeyError):
            return None

    async def get_by_postcode_live(self, postcode: str) -> PlaceInfo | None:
        code = postcode.strip()
        base = _STUBS.get(code)
        if base is None:
            return None
        easting, northing = POSTCODE_LV95.get(code, (2683000, 1248000))
        oev = OeVGueteklasse.NONE
        laerm: float | None = None

        # 1. ARE ÖV-Güteklasse & BAFU Lärm via api3 Identify (federal, all cantons)
        for layer_id in ("ch.are.gueteklassen_oev", "ch.bafu.larm-strassenlaerm_tag"):
            resp = await self._safe_get(
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
            if resp is not None and resp.status_code == 200:
                try:
                    results = resp.json().get("results") or []
                    if "ch.are" in layer_id:
                        parsed = _parse_oev(results)
                        if parsed != OeVGueteklasse.NONE:
                            oev = parsed
                    else:
                        db = _parse_laerm_db(results)
                        if db is not None:
                            laerm = db
                except (ValueError, KeyError, AttributeError):
                    pass

        # 2. Solar: BFE WGS84 building polygon potential (federal, all cantons)
        solar_kwh: float | None = None
        solar_klasse: str | None = None
        lon_wgs, lat_wgs = POSTCODE_WGS84.get(code, (8.534, 47.378))
        if code not in POSTCODE_WGS84:
            try:
                from src.services.geo_converter import lv95_to_wgs84

                _lat, _lon = lv95_to_wgs84(easting, northing)
                lat_wgs, lon_wgs = _lat, _lon
            except ValueError:
                pass

        resp_solar = await self._safe_get(
            API3_IDENTIFY,
            params={
                "geometry": f"{lon_wgs},{lat_wgs}",
                "geometryType": "esriGeometryPoint",
                "layers": "all:ch.bfe.solarenergie-eignung-daecher",
                "tolerance": 10,
                "imageDisplay": "1,1,1",
                "mapExtent": f"{lon_wgs},{lat_wgs},{lon_wgs},{lat_wgs}",
                "sr": 4326,
            },
        )
        if resp_solar is not None and resp_solar.status_code == 200:
            try:
                results = resp_solar.json().get("results") or []
                kwh, klasse = _parse_solar(results)
                if kwh is not None:
                    solar_kwh = kwh
                if klasse is not None:
                    solar_klasse = klasse
            except (ValueError, KeyError, AttributeError):
                pass

        # 3. Canton-specific enrichment (ZH pilot)
        oereb_zone: str | None = None
        steuerfuss = base.steuerfuss_percent
        steuerfuss_src = base.steuerfuss_source

        if base.canton == "ZH":
            # ZH WFS Nutzungsplanung
            resp_oereb = await self._safe_get(
                ZH_WFS_URL,
                params={
                    "SERVICE": "WFS",
                    "VERSION": "2.0.0",
                    "REQUEST": "GetFeature",
                    "TYPENAMES": "ms:Nutzungsplanung",
                    "BBOX": f"{easting},{northing},{easting+100},{northing+100},EPSG:2056",
                    "COUNT": 5,
                },
            )
            if resp_oereb is not None and resp_oereb.status_code == 200:
                zone = _parse_oereb_xml(resp_oereb.text)
                if zone is not None:
                    oereb_zone = zone

            # ZH Steuerfuss live
            resp_st = await self._safe_get(ZH_STEUER_URL)
            if resp_st is not None and resp_st.status_code == 200:
                parsed_pct, parsed_src = _parse_zh_steuerfuss_html(resp_st.text)
                if parsed_pct is not None:
                    steuerfuss = parsed_pct
                    steuerfuss_src = parsed_src or "zh-steueramt-html"

        # ADR-020: risk scoring (deterministic, no upstream dependency)
        risk_level, risk_reason = self._risk_for(base, steuerfuss, laerm, solar_kwh, oereb_zone)

        return PlaceInfo(
            postcode=code,
            municipality=base.municipality,
            canton=base.canton,
            steuerfuss_percent=steuerfuss,
            noise_db_day=laerm if laerm is not None else base.noise_db_day,
            oev_class=oev if oev != OeVGueteklasse.NONE else base.oev_class,
            gwr_building_count=base.gwr_building_count,
            solar_kwh_m2=solar_kwh,
            solar_class=solar_klasse,
            oereb_zone=oereb_zone,
            steuerfuss_source=steuerfuss_src,
            risk_level=risk_level,
            risk_reason=risk_reason,
        )

    @staticmethod
    def _risk_for(
        base: PlaceInfo,
        steuerfuss: float | None,
        laerm: float | None,
        solar_kwh: float | None,
        oereb_zone: str | None,
    ) -> tuple[str | None, str | None]:
        """ADR-020 risk heuristic: high/medium/low + reason (5 words max).

        Rules (in priority order):
        - Kernzone → high (ÖREB preservation)
        - Lärm >70 dB → high, >60 dB → medium
        - Solar sehr gut + low noise → low (good micro-location)
        - Otherwise medium for non-trivial, low when everything quiet.
        """
        laerm_eff = laerm if laerm is not None else base.noise_db_day
        zone = (oereb_zone or base.oereb_zone or "").lower()
        if "kernzone" in zone:
            return "high", "Kernzone — heightened preservation requirements"
        if laerm_eff is not None:
            if laerm_eff > 70:
                return "high", "Straßenlärm >70 dB — elevated noise exposure"
            if laerm_eff > 60:
                return "medium", "Straßenlärm >60 dB — moderate noise exposure"
        if solar_kwh is not None and solar_kwh >= 1200 and (laerm_eff is None or laerm_eff < 55):
            return "low", "Sehr gut solar + quiet location"
        # Default: low when nothing elevated
        if laerm_eff is not None and laerm_eff >= 55:
            return "medium", "Moderate environmental indicators"
        return "low", "No elevated indicator"
