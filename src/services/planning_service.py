"""Planning service — SQLite-backed Baugesuch store + Amtsblatt fetch."""

from __future__ import annotations

from datetime import date

from src.db.planning_repo import PlanningRepo
from src.models.planning import Baugesuch
from src.services.amtsblatt_service import AmtsblattService
from src.services.ogd_service import OgdService


class PlanningService:
    """Store + query Baugesuche (SQLite persistent, TTL via auflage_end).

    In-memory fallback kept via repo indirection — tests use :memory:.
    """

    def __init__(
        self,
        fetcher: AmtsblattService | None = None,
        repo: PlanningRepo | None = None,
        ogd: OgdService | None = None,
    ) -> None:
        self._fetcher = fetcher or AmtsblattService()
        self._repo = repo or PlanningRepo()
        self._ogd = ogd

    def seed(self, items: list[Baugesuch]) -> None:
        """Seed for tests / demo (upserts)."""
        self._repo.upsert_many(items)

    def list_items(
        self,
        postcode: str | None = None,
        active_only: bool = True,
        on: date | None = None,
    ) -> list[Baugesuch]:
        return self._repo.list_items(postcode=postcode, active_only=active_only, on=on)

    def get_by_postcode(
        self, postcode: str, active_only: bool = True, on: date | None = None
    ) -> list[Baugesuch]:
        return self.list_items(postcode=postcode, active_only=active_only, on=on)

    def find_by_radius(
        self,
        lat: float,
        lon: float,
        radius_m: float = 1000.0,
        active_only: bool = True,
        on: date | None = None,
    ) -> list[tuple[Baugesuch, float]]:
        return self._repo.find_by_radius(
            lat=lat, lon=lon, radius_m=radius_m, active_only=active_only, on=on
        )

    def find_by_bbox(
        self,
        min_lat: float,
        min_lon: float,
        max_lat: float,
        max_lon: float,
        active_only: bool = True,
        on: date | None = None,
    ) -> list[Baugesuch]:
        return self._repo.find_by_bbox(
            min_lat=min_lat,
            min_lon=min_lon,
            max_lat=max_lat,
            max_lon=max_lon,
            active_only=active_only,
            on=on,
        )

    async def refresh(self, canton: str = "ZH", since: date | None = None) -> int:
        """Poll Amtsblatt and upsert — returns count."""
        items = await self._fetcher.fetch_publications(canton=canton, since=since)
        if items:
            self._repo.upsert_many(items)
        return len(items)

    async def backfill_ogd(self) -> int:
        """Fetch OGD 2982 CSV and upsert — returns count (ADR-009 hibrid B)."""
        ogd = self._ogd or OgdService()
        items = await ogd.fetch_csv()
        if items:
            self._repo.upsert_many(items)
        return len(items)
