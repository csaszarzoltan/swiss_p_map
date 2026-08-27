"""Ort expansion RED→GREEN — solar + oereb live (ADR-007)."""

import httpx
import pytest

from src.services.place_service import PlaceService


@pytest.mark.asyncio
async def test_place_live_8004_solar_and_oereb() -> None:
    """Mocked api3 Identify → PlaceInfo solar>100 + oereb W2 for 8004."""
    def handler(request: httpx.Request) -> httpx.Response:
        params = dict(request.url.params)
        layers = params.get("layers", "")
        if "ch.bfe.solarenergie" in layers:
            return httpx.Response(
                200,
                json={"results": [{"layerBodId": "ch.bfe.solarenergie-eignung-daecher",
                                   "properties": {"kwh_m2": "1400", "klasse": "sehr gut"}}]},
            )
        if "ch.vd.oereb" in layers:
            return httpx.Response(
                200,
                json={"results": [{"layerBodId": "ch.vd.oereb",
                                   "properties": {"zone": "W2 Wohnzone", "nutzungszone": "W2"}}]},
            )
        if "ch.are" in layers:
            return httpx.Response(
                200,
                json={"results": [{"layerBodId": "ch.are.gueteklassen_oev",
                                   "properties": {"klasse": "A"}}]},
            )
        if "ch.bafu" in layers:
            return httpx.Response(
                200,
                json={"results": [{"layerBodId": "ch.bafu.larm-strassenlaerm_tag",
                                   "properties": {"Lr_Tag": "65-70"}}]},
            )
        return httpx.Response(200, json={"results": []})

    transport = httpx.MockTransport(handler)
    async with httpx.AsyncClient(transport=transport) as client:
        svc = PlaceService(client=client)
        info = await svc.get_by_postcode_live("8004")
        assert info is not None
        assert info.solar_kwh_m2 is not None and info.solar_kwh_m2 >= 100
        assert info.solar_class is not None
        assert info.oereb_zone is not None and "W2" in info.oereb_zone
        assert info.oev_class.value == "A"
        assert info.noise_db_day is not None
