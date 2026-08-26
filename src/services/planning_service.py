"""Planning service — in-memory Baugesuch store + fetch via AmtsblattService."""

from __future__ import annotations

from datetime import date

from src.models.planning import Baugesuch
from src.services.amtsblatt_service import AmtsblattService


class PlanningService:
    """Store + query Baugesuche (MVP: in-memory, TTL via is_active).

    SQLite perzisztencia külön kártya; a felület stabil marad.
    """

    def __init__(self, fetcher: AmtsblattService | None = None) -> None:
        self._fetcher = fetcher or AmtsblattService()
        self._items: list[Baugesuch] = []

    def seed(self, items: list[Baugesuch]) -> None:
        """Seed for tests / demo (idempotent — replaces)."""
        self._items = list(items)

    def list_items(self, postcode: str | None = None, active_only: bool = True, on: date | None = None) -> list[Baugesuch]:
        ref = on or date.today()  # noqa: DTZ011 — MVP in-memory store, wall-clock is intentional; SQLite task will use injected 'on'
        out = self._items
        if postcode:
            code = postcode.strip()
            out = [b for b in out if b.postcode == code]
        if active_only:
            out = [b for b in out if b.is_active(ref)]
        return out

    def get_by_postcode(self, postcode: str, active_only: bool = True, on: date | None = None) -> list[Baugesuch]:
        return self.list_items(postcode=postcode, active_only=active_only, on=on)

    async def refresh(self, canton: str = "ZH", since: date | None = None) -> int:
        """Poll Amtsblatt and replace store — returns count."""
        items = await self._fetcher.fetch_publications(canton=canton, since=since)
        self._items = items
        return len(items)
