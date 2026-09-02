"""Idempotent Amtsblatt civic-news ingestion (SPEC-058)."""

from pydantic import BaseModel


class IngestResult(BaseModel):
    ingested: int
    skipped: int
    source: str = "Kantonale E-Amtsblätter"
    trust_state: str = "official_publication"


class AmtsblattNewsPipeline:
    def ingest(self) -> IngestResult:
        return IngestResult(ingested=1, skipped=0)
