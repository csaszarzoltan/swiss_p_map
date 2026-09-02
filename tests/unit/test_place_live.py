"""Place live OGD — RED: api3 Identify + ZH finance (ADR-005)."""

import httpx
import pytest

from src.services.place_service import PlaceService


@pytest.mark.asyncio
async def test_place_live_8004_ov_a_and_laerm() -> None:
    """Mocked api3 Identify → PlaceInfo ÖV=A, Lärm>60, GWR>0 for 8004."""
    # Order: geocode not called (hardcoded LV95), then 2x identify
    calls: list[str] = []

    def handler(request: httpx.Request) -> httpx.Response:
        url = str(request.url)
        calls.append(url)
        params = dict(request.url.params)
        layers = params.get("layers", "")
        if "ch.are.gueteklassen_oev" in layers or "ch.are" in url:
            return httpx.Response(
                200,
                json={
                    "results": [
                        {
                            "layerBodId": "ch.are.gueteklassen_oev",
                            "properties": {"klasse": "A", "label": "A – sehr gut"},
                        }
                    ]
                },
            )
        if "ch.bafu.larm" in layers or "ch.bafu" in url or "larm" in url.lower():
            return httpx.Response(
                200,
                json={
                    "results": [
                        {
                            "layerBodId": "ch.bafu.larm-strassenlaerm_tag",
                            "properties": {"Lr_Tag": "65-70", "label": "65-70 dB"},
                        }
                    ]
                },
            )
        # fallback: empty
        return httpx.Response(200, json={"results": []})

    transport = httpx.MockTransport(handler)
    async with httpx.AsyncClient(transport=transport) as client:
        svc = PlaceService(client=client)
        info = await svc.get_by_postcode_live("8004")
        assert info is not None
        assert info.postcode == "8004"
        assert info.oev_class.value == "A"
        assert info.noise_db_day is not None and info.noise_db_day >= 60
        assert info.gwr_building_count is not None
