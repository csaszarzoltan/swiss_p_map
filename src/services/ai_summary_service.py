"""AI summary — 2-mondatos KI-ZUSAMMENFASSUNG 4 nyelven gateway-en át."""

from __future__ import annotations

import json
import os
from typing import Protocol

import httpx

GATEWAY_URL = os.environ.get(
    "SWISSPM_AI_GATEWAY_URL", "http://127.0.0.1:8013/v1/chat/completions"
)
SYSTEM_TMPL = {
    "de": "Du bist KI-ZUSAMMENFASSUNG für Swiss P Map. Fasse in 2 kurzen Sätzen auf Deutsch zusammen, nur aus dem JSON. Am Ende in Klammern: Quelle.",
    "en": "You are AI Summary for Swiss P Map. Summarize in 2 short sentences in English, only from the JSON. Add source in brackets at end.",
    "fr": "Tu es résumé IA pour Swiss P Map. Résume en 2 phrases courtes en français, uniquement à partir du JSON. Source entre crochets à la fin.",
    "it": "Sei riassunto IA per Swiss P Map. Riassumi in 2 frasi brevi in italiano, solo dal JSON. Fonte tra parentesi alla fine.",
}


class HttpPostClient(Protocol):
    async def post(
        self, url: str, json: dict[str, object], headers: dict[str, str] | None = None
    ) -> httpx.Response: ...


def build_prompt(
    locale: str,
    postcode: str,
    place: dict[str, object],
    politics: dict[str, object],
    baugesuche: list[dict[str, object]],
) -> tuple[str, str]:
    loc = locale if locale in SYSTEM_TMPL else "de"
    system = SYSTEM_TMPL[loc]
    payload = json.dumps(
        {
            "postcode": postcode,
            "place": place,
            "politics": politics,
            "baugesuche": baugesuche[:4],
        },
        ensure_ascii=False,
    )
    user = f"JSON:\n{payload}\n\nAufgabe: 2 Sätze, Sprache={loc}, nur JSON, Quelle in Klammern."
    return system, user


class AiSummaryService:
    """Gateway-en át 2 mondat, fallback nélkül (hívó dönt)."""

    def __init__(
        self, client: httpx.AsyncClient | None = None, gateway_url: str | None = None
    ) -> None:
        self._client = client
        self._url = gateway_url or GATEWAY_URL

    async def summarize(
        self,
        locale: str,
        postcode: str,
        place: dict[str, object],
        politics: dict[str, object],
        baugesuche: list[dict[str, object]],
    ) -> str | None:
        """Gateway hívás; hiba/timeout → None (hívó fallbackel sablonra)."""
        system, user = build_prompt(locale, postcode, place, politics, baugesuche)
        body = {
            "model": os.environ.get("SWISSPM_AI_MODEL", "openai/gpt-4o-mini"),
            "messages": [
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
            "max_tokens": 180,
            "temperature": 0.2,
        }
        try:
            if self._client is not None:
                resp = await self._client.post(
                    self._url, json=body, headers={"Content-Type": "application/json"}
                )
            else:
                async with httpx.AsyncClient(timeout=12) as c:
                    resp = await c.post(
                        self._url,
                        json=body,
                        headers={"Content-Type": "application/json"},
                    )
            if resp.status_code != 200:
                return None
            data = resp.json()
            choices = data.get("choices") or []
            if not choices:
                return None
            msg = choices[0].get("message") or {}
            text = (msg.get("content") or "").strip()
            return text if text else None
        except (httpx.HTTPError, ValueError, KeyError, AttributeError):
            return None
