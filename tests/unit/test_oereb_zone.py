"""ADR-023/C: OEREB Nutzungsplanung live zone query (kanton-tudatos).

RED: OerebService (geodienste.ch OGC API, LV95 bbox-builder a WGS84
keplet 0.36-os formaval), kanton-detektolas, honest source_pending
ures feed eseten, 24h cache, 15s timeout, kontrollalt 503.

Live smoke: csak SWISSPM_LIVE=1 eseten fut (CI opt-in), nem unit.
"""

from __future__ import annotations

import os

import httpx
import pytest

from src.services.oereb_service import (
    OerebProviderError,
    OerebService,
    OerebZoneResult,
    build_lv95_bbox,
    wgs84_to_lv95,
)

# Geneve Pont-Rouge kornyeke (OGC API feed van, rechtsstatus inKraft)
_GE_LAT = 46.210
_GE_LON = 6.147


def _ogc_items_handler(request: httpx.Request) -> httpx.Response:
    url = str(request.url)
    assert "bbox-crs=http" in url, f"bbox-crs hianyzik: {url}"
    assert "crs=http" in url, f"crs hianyzik: {url}"
    assert "2056" in url, f"LV95 (2056) hianyzik: {url}"
    assert request.url.params.get("limit"), "limit hianyzik"
    return httpx.Response(
        200,
        json={
            "type": "FeatureCollection",
            "features": [
                {
                    "type": "Feature",
                    "geometry": {"type": "Polygon", "coordinates": []},
                    "properties": {
                        "hauptnutzung_bezeichnung": "Mischzonen",
                        "hauptnutzung_code": 13,
                        "rechtsstatus": "inKraft",
                        "kanton": "GE",
                        "typ_kantonal_bezeichnung": "Zone de developpement 3",
                        "typ_kantonal_code": "13",
                        "typ_kommunal_bezeichnung": "Zone de developpement 3",
                        "typ_kommunal_code": "13",
                    },
                }
            ],
        },
    )


def _empty_items_handler(request: httpx.Request) -> httpx.Response:
    return httpx.Response(
        200, json={"type": "FeatureCollection", "features": []}
    )


def _canton_handler(request: httpx.Request) -> httpx.Response:
    return httpx.Response(
        200,
        json={"results": [{"properties": {"ak": "GE", "name": "Geneve"}}]},
    )


def _error_handler(request: httpx.Request) -> httpx.Response:
    return httpx.Response(500, json={"error": "upstream exploded"})


def _svc(handler: object) -> OerebService:
    transport = httpx.MockTransport(handler)  # type: ignore[arg-type]
    client = httpx.AsyncClient(transport=transport)
    return OerebService(client=client)


def test_wgs84_to_lv95_roundtrip_uses_036_formula() -> None:
    """WGS84 -> LV95 a hivatalos 0.36-os taggal, roundtrip <=2m."""
    e, n = wgs84_to_lv95(_GE_LAT, _GE_LON)
    from src.services.geo_converter import lv95_to_wgs84

    lat2, lon2 = lv95_to_wgs84(e, n)
    e2, n2 = wgs84_to_lv95(lat2, lon2)
    assert abs(e2 - e) <= 2.0
    assert abs(n2 - n) <= 2.0


def test_build_lv95_bbox_lv95_crs_mandatory() -> None:
    """bbox-builder: LV95 E,N sorrend + bbox-crs + crs, 2056."""
    params = build_lv95_bbox(_GE_LAT, _GE_LON, half_m=200.0)
    assert params["bbox-crs"].endswith("/2056")
    assert params["crs"].endswith("/2056")
    e, n = wgs84_to_lv95(_GE_LAT, _GE_LON)
    xmin, ymin, xmax, ymax = (float(v) for v in params["bbox"].split(","))
    assert xmin < e < xmax and ymin < n < ymax
    assert (xmax - xmin) == pytest.approx(400.0)
    assert (ymax - ymin) == pytest.approx(400.0)


def test_build_lv95_bbox_rejects_out_of_switzerland() -> None:
    with pytest.raises(ValueError, match="LV95"):
        build_lv95_bbox(48.85, 2.35)  # Paris


@pytest.mark.asyncio
async def test_zone_live_shape_ge() -> None:
    """Hermetikus mock: GE pont -> Mischzonen + kanton + source meta."""
    svc = _svc(_ogc_items_handler)
    try:
        res = await svc.zone(_GE_LAT, _GE_LON)
    finally:
        await svc.aclose()
    assert isinstance(res, OerebZoneResult)
    assert res.hauptnutzung_bezeichnung == "Mischzonen"
    assert res.hauptnutzung_code == 13
    assert res.rechtsstatus == "inKraft"
    assert res.kanton == "GE"
    assert res.trust_state == "official_measurement"
    assert "geodienste" in res.source
    assert res.fetched_at
    assert res.cache_ttl_seconds == 24 * 3600


@pytest.mark.asyncio
async def test_zone_empty_feed_honest_source_pending() -> None:
    """Ures feed (pl. ZH) -> source_pending + hivatalos-link, NEM hamis adat."""
    svc = _svc(_empty_items_handler)
    try:
        res = await svc.zone(47.378, 8.534)
    finally:
        await svc.aclose()
    assert res.trust_state == "source_pending"
    assert res.hauptnutzung_bezeichnung is None
    assert res.hauptnutzung_code is None
    assert res.source
    assert res.official_url.startswith("http")
    assert "cadastre" in res.official_url or "zh" in res.official_url.lower()


@pytest.mark.asyncio
async def test_zone_provider_error_raises_controlled() -> None:
    svc = _svc(_error_handler)
    try:
        with pytest.raises(OerebProviderError):
            await svc.zone(_GE_LAT, _GE_LON)
    finally:
        await svc.aclose()


@pytest.mark.asyncio
async def test_zone_cache_24h_single_fetch() -> None:
    """Masodik azonos lekerdezes nem indit uj HTTP-hivast (24h cache)."""
    calls: list[str] = []

    def counting(request: httpx.Request) -> httpx.Response:
        calls.append(str(request.url))
        return _ogc_items_handler(request)

    svc = _svc(counting)
    try:
        first = await svc.zone(_GE_LAT, _GE_LON)
        second = await svc.zone(_GE_LAT, _GE_LON)
    finally:
        await svc.aclose()
    assert len(calls) == 1
    assert first.fetched_at == second.fetched_at


@pytest.mark.asyncio
async def test_detect_canton_uses_swisstopo_identify() -> None:
    svc = _svc(_canton_handler)
    try:
        assert await svc.detect_canton(2500294.0, 1118466.0) == "GE"
    finally:
        await svc.aclose()


@pytest.mark.asyncio
async def test_detect_canton_falls_back_none_on_error() -> None:
    svc = _svc(_error_handler)
    try:
        assert await svc.detect_canton(2500294.0, 1118466.0) is None
    finally:
        await svc.aclose()


@pytest.mark.asyncio
async def test_live_smoke_only_with_opt_in() -> None:
    """Elo smoke: csak SWISSPM_LIVE=1 eseten fut (CI opt-in)."""
    if os.environ.get("SWISSPM_LIVE") != "1":
        pytest.skip("live smoke csak SWISSPM_LIVE=1 eseten")
    svc = OerebService()
    try:
        res = await svc.zone(_GE_LAT, _GE_LON)
    finally:
        await svc.aclose()
    assert res.trust_state == "official_measurement"
    assert res.hauptnutzung_bezeichnung
    assert res.kanton == "GE"
