"""SQLite repo for Baugesuche — ADR-002 SQLite MVP.

In-memory fallback (db_path=:memory:) perfect for tests.
Production: data/swisspm.db (WAL, soft TTL via auflage_end filter).
"""

from __future__ import annotations

import sqlite3
from datetime import date
from pathlib import Path

from src.models.planning import Baugesuch

_DDL = """
CREATE TABLE IF NOT EXISTS baugesuche (
    id TEXT PRIMARY KEY,
    title TEXT NOT NULL,
    municipality TEXT NOT NULL,
    municipality_id INTEGER,
    postcode TEXT NOT NULL,
    canton TEXT NOT NULL,
    publication_date TEXT NOT NULL,
    expiration_date TEXT NOT NULL,
    auflage_start TEXT NOT NULL,
    auflage_end TEXT NOT NULL,
    source_url TEXT NOT NULL,
    geocode_precision TEXT NOT NULL DEFAULT 'none',
    lat REAL,
    lon REAL
);
CREATE INDEX IF NOT EXISTS idx_baugesuche_postcode ON baugesuche(postcode);
CREATE INDEX IF NOT EXISTS idx_baugesuche_auflage_end ON baugesuche(auflage_end);
"""


def _row_to_bg(row: sqlite3.Row) -> Baugesuch:
    return Baugesuch(
        id=row["id"],
        title=row["title"],
        municipality=row["municipality"],
        municipality_id=row["municipality_id"],
        postcode=row["postcode"],
        canton=row["canton"],
        publication_date=date.fromisoformat(row["publication_date"]),
        expiration_date=date.fromisoformat(row["expiration_date"]),
        auflage_start=date.fromisoformat(row["auflage_start"]),
        auflage_end=date.fromisoformat(row["auflage_end"]),
        source_url=row["source_url"],
        geocode_precision=row["geocode_precision"] or "none",
        lat=row["lat"],
        lon=row["lon"],
    )


class PlanningRepo:
    """Baugesuch persistence — SQLite, upsert-many + filtered list."""

    def __init__(self, db_path: str = "data/swisspm.db") -> None:
        self._db_path = db_path
        if db_path != ":memory:":
            Path(db_path).parent.mkdir(parents=True, exist_ok=True)
        # Keep single connection for :memory: (each new connect would be empty)
        self._conn = sqlite3.connect(db_path, check_same_thread=False)
        self._conn.row_factory = sqlite3.Row
        self._conn.executescript(_DDL)
        self._conn.commit()

    def upsert_many(self, items: list[Baugesuch]) -> int:
        if not items:
            return 0
        self._conn.executemany(
            """
            INSERT INTO baugesuche
              (id,title,municipality,municipality_id,postcode,canton,
               publication_date,expiration_date,auflage_start,auflage_end,
               source_url,geocode_precision,lat,lon)
            VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?)
            ON CONFLICT(id) DO UPDATE SET
              title=excluded.title, municipality=excluded.municipality,
              municipality_id=excluded.municipality_id, postcode=excluded.postcode,
              canton=excluded.canton, publication_date=excluded.publication_date,
              expiration_date=excluded.expiration_date, auflage_start=excluded.auflage_start,
              auflage_end=excluded.auflage_end, source_url=excluded.source_url,
              geocode_precision=excluded.geocode_precision, lat=excluded.lat, lon=excluded.lon
            """,
            [
                (
                    b.id,
                    b.title,
                    b.municipality,
                    b.municipality_id,
                    b.postcode,
                    b.canton,
                    b.publication_date.isoformat(),
                    b.expiration_date.isoformat(),
                    (b.auflage_start or b.publication_date).isoformat(),
                    (b.auflage_end or b.publication_date).isoformat(),
                    b.source_url,
                    b.geocode_precision,
                    b.lat,
                    b.lon,
                )
                for b in items
            ],
        )
        self._conn.commit()
        return len(items)

    def list_items(
        self,
        postcode: str | None = None,
        active_only: bool = True,
        on: date | None = None,
    ) -> list[Baugesuch]:
        ref = (on or date.today()).isoformat()  # noqa: DTZ011
        where: list[str] = []
        params: list[str] = []
        if postcode:
            where.append("postcode = ?")
            params.append(postcode.strip())
        if active_only:
            where.append("auflage_end >= ?")
            params.append(ref)
            where.append("auflage_start <= ?")
            params.append(ref)
        sql = "SELECT * FROM baugesuche"
        if where:
            sql += " WHERE " + " AND ".join(where)
        sql += " ORDER BY publication_date DESC"
        rows = self._conn.execute(sql, params).fetchall()
        return [_row_to_bg(r) for r in rows]
