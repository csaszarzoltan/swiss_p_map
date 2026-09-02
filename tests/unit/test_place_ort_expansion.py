"""Ort expansion RED→GREEN — solar + oereb live (ADR-007 + ZH WFS)."""

import httpx
import pytest

from src.services.place_service import PlaceService


@pytest.mark.asyncio
async def test_place_live_8004_solar_and_oereb() -> None:
    """Mocked BFE solar + ZH WFS Nutzungsplanung → PlaceInfo solar>100 + oereb Kernzone."""
    wfs_xml = """<?xml version='1.0' encoding="UTF-8" ?><wfs:FeatureCollection xmlns:wfs="http://www.opengis.net/wfs/2.0"><wfs:member><ms:nutzungsplanung xmlns:ms="http://mapserver.gis.umn.edu/mapserver"><ms:typ_gde_bezeichnung>Kernzone</ms:typ_gde_bezeichnung></ms:nutzungsplanung></wfs:member></wfs:FeatureCollection>"""

    def handler(request: httpx.Request) -> httpx.Response:
        url = str(request.url)
        params = dict(request.url.params)
        layers = params.get("layers", "")
        if "ch.bfe.solarenergie" in layers:
            return httpx.Response(
                200,
                json={
                    "results": [
                        {
                            "layerBodId": "ch.bfe.solarenergie-eignung-daecher",
                            "properties": {"kwh_m2": "1400", "klasse": "sehr gut"},
                        }
                    ]
                },
            )
        if "OerebKataster" in url or "WFS" in url or "TYPENAMES" in str(params):
            return httpx.Response(
                200,
                content=wfs_xml.encode(),
                headers={"content-type": "application/xml"},
            )
        if "steuer" in url or "zh.ch" in url:
            return httpx.Response(
                200,
                content=b"<html>Zuerrich 119 %</html>",
                headers={"content-type": "text/html"},
            )
        if "ch.are" in layers:
            return httpx.Response(
                200,
                json={
                    "results": [
                        {
                            "layerBodId": "ch.are.gueteklassen_oev",
                            "properties": {"klasse": "A"},
                        }
                    ]
                },
            )
        if "ch.bafu" in layers:
            return httpx.Response(
                200,
                json={
                    "results": [
                        {
                            "layerBodId": "ch.bafu.larm-strassenlaerm_tag",
                            "properties": {"Lr_Tag": "65-70"},
                        }
                    ]
                },
            )
        return httpx.Response(200, json={"results": []})

    transport = httpx.MockTransport(handler)
    async with httpx.AsyncClient(transport=transport) as client:
        svc = PlaceService(client=client)
        info = await svc.get_by_postcode_live("8004")
        assert info is not None
        assert info.solar_kwh_m2 is not None and info.solar_kwh_m2 >= 100
        assert info.solar_class is not None
        assert info.oereb_zone is not None and "Kernzone" in info.oereb_zone
        assert info.oev_class.value == "A"
        assert info.noise_db_day is not None
