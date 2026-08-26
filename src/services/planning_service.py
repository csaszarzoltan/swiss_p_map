"""Planning service — SQLite-backed Baugesuch store + Amtsblatt fetch."""

from __future__ import annotations

from datetime import date

from src.db.planning_repo import PlanningRepo
from src.models.planning import Baugesuch
from src.services.amtsblatt_service import AmtsblattService


class PlanningService:
    """Store + query Baugesuche (SQLite persistent, TTL via auflage_end).

    In-memory fallback kept via repo indirection — tests use :memory:.
    """

    def __init__(
        self,
        fetcher: AmtsblattService | None = None,
        repo: PlanningRepo | None = None,
    ) -> None:
        self._fetcher = fetcher or AmtsblattService()
        self._repo = repo or PlanningRepo()

    def seed(self, items: list[Baugesuch]) -> None:
        """Seed for tests / demo (upserts)."""
        self._repo.upsert_many(items)

    def list_items(self, postcode: str | None = None, active_only: bool = True, on: date | None = None) -> list[Baugesuch]:
        return self._repo.list_items(postcode=postcode, active_only=active_only, on=on)

    def get_by_postcode(self, postcode: str, active_only: bool = True, on: date | None = None) -> list[Baugesuch]:
        return self.list_items(postcode=postcode, active_only=active_only, on=on)

    async def refresh(self, canton: str = "ZH", since: date | None = None) -> int:
        """Poll Amtsblatt and upsert — returns count."""
        items = await self._fetcher.fetch_publications(canton=canton, since=since)
        if items:
            self._repo.upsert_many(items)
        return len(items)
