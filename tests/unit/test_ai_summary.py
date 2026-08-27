"""AI summary RED→GREEN — gateway mock."""

import httpx
import pytest

from src.services.ai_summary_service import AiSummaryService


@pytest.mark.asyncio
async def test_ai_summary_gateway_mock_de() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        assert "chat/completions" in str(request.url)
        return httpx.Response(200, json={"choices": [{"message": {"content": "In 8004 zahlst du 119% bei 62.5 dB (ÖV A). 2 Baugesuche offen — Muster Anna (SP) vertritt 4+5. (Quelle: api)"}}]})

    transport = httpx.MockTransport(handler)
    async with httpx.AsyncClient(transport=transport) as client:
        svc = AiSummaryService(client=client)
        txt = await svc.summarize("de", "8004", {"postcode": "8004"}, {"district_name": "4+5"}, [])
        assert txt is not None and "8004" in txt


@pytest.mark.asyncio
async def test_ai_summary_gateway_500_fallback_none() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(500, json={"error": "cooldown"})

    transport = httpx.MockTransport(handler)
    async with httpx.AsyncClient(transport=transport) as client:
        svc = AiSummaryService(client=client)
        txt = await svc.summarize("de", "8004", {}, {}, [])
        assert txt is None
