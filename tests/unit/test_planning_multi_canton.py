"""Tesztek a többkantonos építési engedelyekhez (ADR-014)."""

from datetime import date, timedelta

from src.db.planning_repo import PlanningRepo
from src.models.planning import Baugesuch
from src.services.planning_service import PlanningService


def _seed_bsc_be_ge() -> PlanningService:
    """In-memory PlanningService seed - teszteléshez, nem a live DB-től függ."""
    repo = PlanningRepo(db_path=":memory:")
    svc = PlanningService(repo=repo)
    today = date.today()  # noqa: DTZ011
    svc.seed(
        [
            Baugesuch(
                id="test-be-1",
                title="Kramgasse 45, 3011 Bern",
                municipality="Bern",
                municipality_id=351,
                postcode="3011",
                canton="BE",
                publication_date=today - timedelta(days=4),
                expiration_date=today + timedelta(days=361),
                auflage_start=today - timedelta(days=4),
                auflage_end=today + timedelta(days=16),
                source_url="https://test",
                geocode_precision="address",
                lat=46.948,
                lon=7.449,
            ),
            Baugesuch(
                id="test-bs-1",
                title="Freie Strasse 25, 4001 Basel",
                municipality="Basel",
                municipality_id=2701,
                postcode="4001",
                canton="BS",
                publication_date=today - timedelta(days=6),
                expiration_date=today + timedelta(days=359),
                auflage_start=today - timedelta(days=6),
                auflage_end=today + timedelta(days=14),
                source_url="https://test",
                geocode_precision="address",
                lat=47.556,
                lon=7.591,
            ),
            Baugesuch(
                id="test-ge-1",
                title="Rue du Mont-Blanc 14, 1201 Genève",
                municipality="Genève",
                municipality_id=6621,
                postcode="1201",
                canton="GE",
                publication_date=today - timedelta(days=7),
                expiration_date=today + timedelta(days=358),
                auflage_start=today - timedelta(days=7),
                auflage_end=today + timedelta(days=13),
                source_url="https://test",
                geocode_precision="address",
                lat=46.210,
                lon=6.146,
            ),
        ]
    )
    return svc


class TestMultiCantonPlanning:
    def test_multi_canton_quick_picks(self) -> None:
        """Mind a 3 kanton (BE/BS/GE) elérhető in-memory seedből."""
        svc = _seed_bsc_be_ge()
        for pc, expected_canton in [("3011", "BE"), ("4001", "BS"), ("1201", "GE")]:
            items = svc.list_items(postcode=pc, active_only=True)
            assert len(items) > 0, f"Nincs Baugesuch a {pc} irányítószámhoz!"
            for item in items:
                assert item.canton == expected_canton
                assert item.lat is not None
                assert item.lon is not None
                assert item.auflage_end is not None

    def test_multi_canton_bbox(self) -> None:
        """Térbeli bbox keresés működik több kantonnal."""
        svc = _seed_bsc_be_ge()
        bbox_bern = svc.find_by_bbox(
            min_lat=46.94, max_lat=46.96, min_lon=7.43, max_lon=7.46, active_only=True
        )
        assert len(bbox_bern) > 0, "Nincs Bern bbox találat!"
        assert bbox_bern[0].postcode == "3011"

    def test_live_api_returns_multi_canton(self) -> None:
        """A live API endpoint elérhető és adatai koherensek."""
        from fastapi.testclient import TestClient

        from src.main import app

        client = TestClient(app)
        resp = client.get("/api/v1/planning/baugesuche?postcode=8004&active_only=true")
        assert resp.status_code == 200
        items = resp.json()["items"]
        assert len(items) > 0
        # Minden elemnek van postcode + canton
        for item in items:
            assert item["postcode"] == "8004"
            assert item["canton"] == "ZH"
