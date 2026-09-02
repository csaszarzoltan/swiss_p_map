"""Unified source provenance catalogue for SPEC-029."""

from __future__ import annotations

from datetime import UTC, datetime

from pydantic import BaseModel


class SourceProvenance(BaseModel):
    id: str
    source: str
    trust_state: str
    refreshed_at: str
    status: str = "available"


class ProvenanceService:
    def list_sources(self) -> list[SourceProvenance]:
        stamp = datetime.now(UTC).replace(microsecond=0).isoformat()
        rows = [
            ("bfs-impi", "BFS/FSO IMPI", "modeled_estimate"),
            ("bafu-nabel", "BAFU NABEL", "official_measurement"),
            ("cadastre", "Swisstopo / Kantonale Geoportale", "cadastral_registry"),
            ("sbb", "SBB / OpenData.ch", "official_measurement"),
        ]
        return [
            SourceProvenance(id=i, source=s, trust_state=t, refreshed_at=stamp)
            for i, s, t in rows
        ]
