"""SPEC-047 source-safe local news — served from the shared Amtsblatt store."""

from __future__ import annotations

from datetime import UTC, datetime

from pydantic import BaseModel, Field

from src.db.planning_repo import PlanningRepo

SOURCE = "Kantonale E-Amtsblätter"


class NewsItem(BaseModel):
    id: str
    title: str
    municipality: str
    postcode: str
    canton: str
    publication_date: str
    source: str = SOURCE
    source_url: str
    trust_state: str = "official_publication"
    fetched_at: str = ""


class LocalNewsResponse(BaseModel):
    postcode: str = Field(pattern=r"^\d{4}$")
    items: list[NewsItem]
    status: str
    source: str = SOURCE
    trust_state: str
    fetched_at: str = ""


class LocalNewsService:
    """Serve postcode-filtered news from the shared Amtsblatt store.

    Empty store -> honest ``source_pending``, never fabricated content
    (REQ-047-004). Only Auflage-active items are served (soft TTL).
    """

    def __init__(self, repo: PlanningRepo | None = None) -> None:
        self._repo = repo or PlanningRepo()

    def get_local(self, postcode: str) -> LocalNewsResponse:
        stamp = datetime.now(UTC).isoformat()
        stored = self._repo.list_items(postcode=postcode)
        if not stored:
            return LocalNewsResponse(
                postcode=postcode,
                items=[],
                status="source_pending",
                trust_state="source_pending",
                fetched_at=stamp,
            )
        return LocalNewsResponse(
            postcode=postcode,
            items=[
                NewsItem(
                    id=b.id,
                    title=b.title,
                    municipality=b.municipality,
                    postcode=b.postcode,
                    canton=b.canton,
                    publication_date=b.publication_date.isoformat(),
                    source_url=b.source_url,
                    fetched_at=stamp,
                )
                for b in stored
            ],
            status="success",
            trust_state="official_publication",
            fetched_at=stamp,
        )
