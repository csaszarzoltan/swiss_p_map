"""Amtsblatt civic-news ingestion (SPEC-058) — real XML fetch, idempotent store."""

from __future__ import annotations

from datetime import UTC, datetime

from pydantic import BaseModel

from src.db.planning_repo import PlanningRepo
from src.services.amtsblatt_service import AmtsblattService

SOURCE = "Kantonale E-Amtsblätter"


class IngestResult(BaseModel):
    ingested: int
    skipped: int
    source: str = SOURCE
    trust_state: str = "official_publication"
    fetched_at: str = ""


class AmtsblattNewsPipeline:
    """Poll Amtsblatt XML and upsert into the shared store (idempotent by id).

    The store is shared with ``LocalNewsService`` — POST ingest feeds GET news.
    Re-ingest of known ids is a deduplicated success (REQ-058-006).
    Provider failure / empty feed -> honest ``source_pending``, never
    ``official_measurement`` (REQ-058-004/005).
    """

    def __init__(
        self,
        fetcher: AmtsblattService | None = None,
        repo: PlanningRepo | None = None,
    ) -> None:
        self._fetcher = fetcher or AmtsblattService()
        self._repo = repo or PlanningRepo()

    @property
    def store(self) -> PlanningRepo:
        """Shared store — inject into LocalNewsService to serve ingested items."""
        return self._repo

    async def ingest(self, canton: str = "ZH") -> IngestResult:
        stamp = datetime.now(UTC).isoformat()
        try:
            items = await self._fetcher.fetch_publications(canton=canton)
        except Exception:  # noqa: BLE001 — provider surprise -> honest pending
            items = []
        if not items:
            return IngestResult(
                ingested=0, skipped=0, trust_state="source_pending", fetched_at=stamp
            )
        known = {b.id for b in self._repo.list_items(active_only=False)}
        fresh = [b for b in items if b.id not in known]
        if fresh:
            self._repo.upsert_many(fresh)
        return IngestResult(
            ingested=len(fresh),
            skipped=len(items) - len(fresh),
            fetched_at=stamp,
        )
