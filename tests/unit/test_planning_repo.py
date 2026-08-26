"""Unit: PlanningRepo SQLite — RED Task 5a."""

from datetime import date

from src.db.planning_repo import PlanningRepo
from src.models.planning import Baugesuch


def _sample(id_: str = "test-1", postcode: str = "8004", pub: date = date(2026, 8, 20)) -> Baugesuch:
    return Baugesuch(
        id=id_,
        title="Neubau Test",
        municipality="Zürich",
        municipality_id=261,
        postcode=postcode,
        canton="ZH",
        publication_date=pub,
        expiration_date=date(2027, 8, 20),
        source_url=f"https://amtsblattportal.ch/api/v1/publications/{id_}/xml",
        geocode_precision="locality",
        lat=47.38,
        lon=8.54,
    )


def test_repo_upsert_and_list() -> None:
    repo = PlanningRepo(db_path=":memory:")
    b1 = _sample("a-1", "8004", date(2026, 8, 20))
    b2 = _sample("a-2", "8610", date(2026, 8, 22))
    repo.upsert_many([b1, b2])
    all_items = repo.list_items(active_only=False)
    assert len(all_items) == 2
    filtered = repo.list_items(postcode="8004", active_only=False)
    assert len(filtered) == 1
    assert filtered[0].id == "a-1"


def test_repo_active_filter() -> None:
    repo = PlanningRepo(db_path=":memory:")
    b = _sample("a-3", "8004", date(2026, 8, 20))  # auflage_end 2026-09-09
    repo.upsert_many([b])
    assert len(repo.list_items(active_only=True, on=date(2026, 9, 1))) == 1
    assert len(repo.list_items(active_only=True, on=date(2026, 9, 10))) == 0
    assert len(repo.list_items(active_only=False, on=date(2026, 9, 10))) == 1


def test_repo_upsert_overwrites() -> None:
    repo = PlanningRepo(db_path=":memory:")
    b1 = _sample("same", "8004", date(2026, 8, 20))
    repo.upsert_many([b1])
    b2 = _sample("same", "8004", date(2026, 8, 21))
    b2.title = "Updated"
    repo.upsert_many([b2])
    items = repo.list_items(active_only=False)
    assert len(items) == 1
    assert items[0].title == "Updated"
