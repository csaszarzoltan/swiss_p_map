"""ZH Steuerfuss RED→GREEN — steueramt.zh.ch HTML mock (ADR-008)."""

import httpx
import pytest

from src.services.place_service import PlaceService


@pytest.mark.asyncio
async def test_place_live_zh_steuerfuss_mock_returns_119_and_source() -> None:
    """Mocked zh.ch HTML → 8004 Zürich 119%, source zh-steueramt-html."""
    html = "<html><table><tr><td>Stadt Zürich</td><td>119 %</td></tr></table></html>"

    def handler(request: httpx.Request) -> httpx.Response:
        url = str(request.url)
        if "steuer" in url or "zh.ch" in url:
            return httpx.Response(200, content=html.encode(), headers={"content-type": "text/html"})
        if "ch.are" in url or "gueteklassen" in url:
            return httpx.Response(200, json={"results": []})
        if "ch.bafu" in url:
            return httpx.Response(200, json={"results": []})
        if "ch.bfe" in url:
            return httpx.Response(200, json={"results": []})
        if "oereb" in url.lower():
            return httpx.Response(200, json={"results": []})
        if "api3" in url:
            return httpx.Response(200, json={"results": []})
        return httpx.Response(404, json={"results": []})

    transport = httpx.MockTransport(handler)
    async with httpx.AsyncClient(transport=transport) as client:
        svc = PlaceService(client=client)
        info = await svc.get_by_postcode_live("8004")
        assert info is not None
        # 119% from HTML parse, source rewritten
        assert info.steuerfuss_percent == 119.0
        assert info.steuerfuss_source == "zh-steueramt-html"


@pytest.mark.asyncio
async def test_place_live_zh_steuerfuss_500_fallback_stub() -> None:
    """zh.ch 500 → fallback stub 119.0 source stub."""
    def handler(request: httpx.Request) -> httpx.Response:
        url = str(request.url)
        if "steuer" in url or "zh.ch" in url:
            return httpx.Response(500, content=b"error")
        return httpx.Response(200, json={"results": []})

    transport = httpx.MockTransport(handler)
    async with httpx.AsyncClient(transport=transport) as client:
        svc = PlaceService(client=client)
        info = await svc.get_by_postcode_live("8004")
        assert info is not None
        assert info.steuerfuss_percent == 119.0
        assert info.steuerfuss_source == "stub"
