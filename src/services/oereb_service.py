"""OEREB Nutzungsplanung live zone query — ADR-023/C.

Forras: geodienste.ch OGC API Features
``npl_nutzungsplanung_v1_2_0`` (collection ``grundnutzung``), LV95
(EPSG:2056) bbox + ``bbox-crs`` + ``crs`` parameterekkel.
Eloben validalva 2026-09-24: GE/AI/SO/SZ ad vissza feature-oket
(Wohnzonen/Arbeitszonen/Mischzonen, rechtsstatus inKraft);
ZH/BE ures feedet ad (lefedettseg-hiany, nem hiba).

Kanton-tudatos: a feature hordozza a ``kanton`` mezot; ures feed
eseten a kanton-detektolas swisstopo Identify segitsegevel tortenik
(``ch.swisstopo.swissboundaries3d-kanton-flaeche.fill``).
ZH-ra a meglevo WFS Nutzungsplanung marad (place_service).

Ures feed -> honest ``source_pending`` + hivatalos-link (NEM hamis adat).
"""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Literal

import httpx
from pydantic import BaseModel, Field

from src.services.geo_converter import (
    EASTING_MAX,
    EASTING_MIN,
    NORTHING_MAX,
    NORTHING_MIN,
)

OGC_BASE = (
    "https://geodienste.ch/db/npl_nutzungsplanung_v1_2_0/deu/ogcapi"
)
OGC_ITEMS = f"{OGC_BASE}/collections/grundnutzung/items"
CRS_2056 = "http://www.opengis.net/def/crs/EPSG/0/2056"

CANTON_IDENTIFY = "https://api3.geo.admin.ch/rest/services/api/MapServer/identify"
CANTON_LAYER = "ch.swisstopo.swissboundaries3d-kanton-flaeche.fill"

_TIMEOUT_S = 15.0
_CACHE_TTL_S = 24 * 3600  # zonaterv ritkan valtozik
_HALF_M_DEFAULT = 200.0
_LIMIT = 5

TrustState = Literal["official_measurement", "source_pending"]


class OerebProviderError(RuntimeError):
    """Kontrollalt provider-hiba (timeout / 5xx / ervenytelen payload)."""


def wgs84_to_lv95(lat: float, lon: float) -> tuple[float, float]:
    """WGS84 (EPSG:4326) -> LV95 (EPSG:2056), hivatalos swisstopo kozelites.

    Elore irany (LV95→WGS84) a ``geo_converter.lv95_to_wgs84``-ben;
    ez az inverz irany a 0.36-os taggal
    (``- 0.36 * y * x**2``), roundtrip <=2m.
    """
    lat_s = lat * 3600.0
    lon_s = lon * 3600.0
    y = (lon_s - 26782.5) / 10000.0
    x = (lat_s - 169028.66) / 10000.0
    easting = (
        2600072.37
        + 211455.93 * y
        - 10938.51 * y * x
        - 0.36 * y * x * x
        - 44.54 * y**3
    )
    northing = (
        1200147.07
        + 308807.95 * x
        + 3745.25 * y * y
        + 76.63 * x * x
        - 194.56 * y * y * x
        + 119.79 * x**3
    )
    return easting, northing


def build_lv95_bbox(
    lat: float, lon: float, half_m: float = _HALF_M_DEFAULT
) -> dict[str, str]:
    """LV95 bbox-builder: ``bbox`` + kotelezo ``bbox-crs`` + ``crs`` (2056).

    Raises:
        ValueError: ha a pont Magyarorszagon kivul esik (ervenytelen LV95).
    """
    easting, northing = wgs84_to_lv95(lat, lon)
    if not (EASTING_MIN <= easting <= EASTING_MAX):
        raise ValueError(
            f"easting {easting:.0f} outside LV95 bounds "
            f"[{EASTING_MIN:.0f}, {EASTING_MAX:.0f}]"
        )
    if not (NORTHING_MIN <= northing <= NORTHING_MAX):
        raise ValueError(
            f"northing {northing:.0f} outside LV95 bounds "
            f"[{NORTHING_MIN:.0f}, {NORTHING_MAX:.0f}]"
        )
    return {
        "bbox": (
            f"{easting - half_m},{northing - half_m},"
            f"{easting + half_m},{northing + half_m}"
        ),
        "bbox-crs": CRS_2056,
        "crs": CRS_2056,
        "limit": str(_LIMIT),
        "f": "json",
    }


class OerebZoneResult(BaseModel):
    lat: float
    lon: float
    hauptnutzung_bezeichnung: str | None = None
    hauptnutzung_code: int | None = None
    rechtsstatus: str | None = None
    typ_kantonal_bezeichnung: str | None = None
    typ_kommunal_bezeichnung: str | None = None
    kanton: str | None = Field(default=None, pattern=r"^[A-Z]{2}$")
    source: str = "geodienste.ch OGC API npl_nutzungsplanung_v1_2_0"
    official_url: str = "https://www.cadastre.ch/"
    fetched_at: str
    trust_state: TrustState = "official_measurement"
    cache_ttl_seconds: int = _CACHE_TTL_S


_OFFICIAL_URL_BY_CANTON: dict[str, str] = {
    "ZH": "https://maps.zh.ch/",
}


def _official_url(kanton: str | None) -> str:
    if kanton and kanton in _OFFICIAL_URL_BY_CANTON:
        return _OFFICIAL_URL_BY_CANTON[kanton]
    return "https://www.cadastre.ch/"


def _utcnow() -> str:
    return datetime.now(UTC).isoformat().replace("+00:00", "Z")


class OerebService:
    """Kanton-tudatos OEREB zonale kerdezes (DI-friendly, httpx-injected)."""

    def __init__(self, client: httpx.AsyncClient | None = None) -> None:
        self._client = client
        self._owns_client = client is None
        self._cache: dict[str, OerebZoneResult] = {}

    async def aclose(self) -> None:
        if self._owns_client and self._client is not None:
            await self._client.aclose()
            self._client = None

    def _http(self) -> httpx.AsyncClient:
        if self._client is not None:
            return self._client
        return httpx.AsyncClient(timeout=_TIMEOUT_S)

    @staticmethod
    def _cache_key(lat: float, lon: float) -> str:
        return f"{round(lat, 5)}:{round(lon, 5)}"

    @staticmethod
    def _as_int(value: object) -> int | None:
        if isinstance(value, bool):
            return None
        if isinstance(value, (int, float)):
            return int(value)
        if isinstance(value, str) and value.strip().lstrip("-").isdigit():
            try:
                return int(value.strip())
            except ValueError:
                return None
        return None

    async def detect_canton(self, easting: float, northing: float) -> str | None:
        """Kanton-detektolas swisstopo Identify segitsegevel (``ak`` mezo).

        Hiba eseten None (soha nem emel kivetelt).
        """
        params: dict[str, str | int | float] = {
            "geometry": f"{easting:.1f},{northing:.1f}",
            "geometryType": "esriGeometryPoint",
            "layers": f"all:{CANTON_LAYER}",
            "tolerance": 0,
            "mapExtent": (
                f"{easting - 1000:.0f},{northing - 1000:.0f},"
                f"{easting + 1000:.0f},{northing + 1000:.0f}"
            ),
            "imageDisplay": "100,100,96",
            "sr": 2056,
            "geometryFormat": "geojson",
        }
        try:
            client = self._http()
            owns = self._client is None
            if owns:
                async with client as c:
                    resp = await c.get(CANTON_IDENTIFY, params=params)
            else:
                resp = await client.get(CANTON_IDENTIFY, params=params)
            resp.raise_for_status()
            results = resp.json().get("results") or []
        except (httpx.HTTPError, ValueError, KeyError, AttributeError):
            return None
        for r in results:
            props = r.get("properties") or {}
            if not isinstance(props, dict):
                continue
            ak = props.get("ak")
            if isinstance(ak, str) and len(ak.strip()) == 2:
                return ak.strip().upper()
        return None

    async def zone(
        self, lat: float, lon: float, half_m: float = _HALF_M_DEFAULT
    ) -> OerebZoneResult:
        """Zonale kerdezes lat/lon-ra. Ures feed -> honest source_pending."""
        key = self._cache_key(lat, lon)
        cached = self._cache.get(key)
        if cached is not None:
            return cached

        try:
            params = build_lv95_bbox(lat, lon, half_m=half_m)
        except ValueError as exc:
            raise OerebProviderError(str(exc)) from exc

        try:
            client = self._http()
            owns = self._client is None
            if owns:
                async with client as c:
                    resp = await c.get(OGC_ITEMS, params=params)
            else:
                resp = await client.get(OGC_ITEMS, params=params)
            resp.raise_for_status()
            payload = resp.json()
        except (httpx.HTTPError, ValueError) as exc:
            raise OerebProviderError(
                f"oereb provider unavailable: {exc}"
            ) from exc

        features = payload.get("features") or []
        first = next(
            (
                f
                for f in features
                if isinstance(f, dict) and isinstance(f.get("properties"), dict)
            ),
            None,
        )
        fetched_at = _utcnow()
        if first is None:
            # Ures feed (pl. ZH/BE lefedettseg-hiany): honest pending.
            easting, northing = wgs84_to_lv95(lat, lon)
            kanton = await self.detect_canton(easting, northing)
            result = OerebZoneResult(
                lat=lat,
                lon=lon,
                kanton=kanton,
                source="geodienste.ch OGC API npl_nutzungsplanung_v1_2_0 (empty feed)",
                official_url=_official_url(kanton),
                fetched_at=fetched_at,
                trust_state="source_pending",
            )
            self._cache[key] = result
            return result

        props = first["properties"]
        kanton_raw = props.get("kanton")
        kanton = (
            kanton_raw.strip().upper()
            if isinstance(kanton_raw, str) and len(kanton_raw.strip()) == 2
            else None
        )
        bez = props.get("hauptnutzung_bezeichnung")
        result = OerebZoneResult(
            lat=lat,
            lon=lon,
            hauptnutzung_bezeichnung=(
                bez.strip() if isinstance(bez, str) and bez.strip() else None
            ),
            hauptnutzung_code=self._as_int(props.get("hauptnutzung_code")),
            rechtsstatus=(
                str(props["rechtsstatus"])
                if isinstance(props.get("rechtsstatus"), str)
                else None
            ),
            typ_kantonal_bezeichnung=props.get("typ_kantonal_bezeichnung")
            if isinstance(props.get("typ_kantonal_bezeichnung"), str)
            else None,
            typ_kommunal_bezeichnung=props.get("typ_kommunal_bezeichnung")
            if isinstance(props.get("typ_kommunal_bezeichnung"), str)
            else None,
            kanton=kanton,
            official_url=_official_url(kanton),
            fetched_at=fetched_at,
            trust_state="official_measurement",
        )
        self._cache[key] = result
        return result
