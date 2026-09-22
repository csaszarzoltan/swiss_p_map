"""Séma-migráció tesztek: régi DB (hiányzó oszlopok) -> PlanningRepo induláskor pótolja.

Bug kontextus: a `CREATE TABLE IF NOT EXISTS` nem migrál meglévő táblát, ezért egy
korábbi séma-verziójú `data/swisspm.db`-n az `upsert_many` „table baugesuche has no
column named contractor" hibával elhalt — a demo seed csendben elveszett, és a UI-n
nem jelent meg aktív Baugesuch.
"""

import sqlite3
from pathlib import Path

from src.db.planning_repo import PlanningRepo
from src.models.planning import Baugesuch

# A 2026-08 előtti séma: a contractor/architect/parcel_number/zone_type/risk_level
# oszlopok még nem léteztek.
_LEGACY_DDL = """
CREATE TABLE baugesuche (
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
"""


def _legacy_db(path: str) -> None:
    conn = sqlite3.connect(path)
    conn.executescript(_LEGACY_DDL)
    conn.execute(
        """
        INSERT INTO baugesuche
          (id,title,municipality,municipality_id,postcode,canton,
           publication_date,expiration_date,auflage_start,auflage_end,
           source_url,geocode_precision,lat,lon)
        VALUES ('legacy-1','Alt','Zürich',261,'8004','ZH',
                '2026-08-01','2026-08-10','2026-08-01','2026-08-10',
                'https://test','address',47.37,8.52)
        """
    )
    conn.commit()
    conn.close()


class TestSchemaMigration:
    def test_legacy_db_gets_missing_columns(self, tmp_path: Path) -> None:
        """Régi séma -> a hiányzó oszlopok migráció után megvannak."""
        db = str(tmp_path / "legacy.db")
        _legacy_db(db)

        repo = PlanningRepo(db_path=db)
        columns = {row["name"] for row in repo._conn.execute("PRAGMA table_info(baugesuche)")}
        for column in ("contractor", "architect", "parcel_number", "zone_type", "risk_level"):
            assert column in columns, f"Hiányzó migrált oszlop: {column}"

    def test_upsert_works_on_migrated_legacy_db(self, tmp_path: Path) -> None:
        """Migráció után az upsert (és így a demo seed) nem hal el némán."""
        from datetime import date, timedelta

        db = str(tmp_path / "legacy.db")
        _legacy_db(db)
        repo = PlanningRepo(db_path=db)

        today = date.today()  # noqa: DTZ011
        repo.upsert_many(
            [
                Baugesuch(
                    id="demo-8004-1",
                    title="Badenerstrasse 120, 8004 Zürich",
                    municipality="Zürich",
                    municipality_id=261,
                    postcode="8004",
                    canton="ZH",
                    publication_date=today - timedelta(days=2),
                    expiration_date=today + timedelta(days=363),
                    auflage_start=today - timedelta(days=2),
                    auflage_end=today + timedelta(days=18),
                    source_url="https://test",
                    geocode_precision="address",
                    lat=47.37,
                    lon=8.52,
                    contractor="Test AG",
                    architect="Test Architekten",
                    parcel_number="GB 1",
                    zone_type="Kernzone",
                    risk_level="high",
                )
            ]
        )

        items = repo.list_items(postcode="8004", active_only=True)
        assert len(items) == 1
        assert items[0].contractor == "Test AG"
        assert items[0].risk_level == "high"

    def test_migration_is_idempotent(self, tmp_path: Path) -> None:
        """Ismételt indulás nem hibázik és nem duplikál oszlopot."""
        db = str(tmp_path / "legacy.db")
        _legacy_db(db)

        PlanningRepo(db_path=db)
        repo = PlanningRepo(db_path=db)
        columns = [row["name"] for row in repo._conn.execute("PRAGMA table_info(baugesuche)")]
        assert columns.count("risk_level") == 1
