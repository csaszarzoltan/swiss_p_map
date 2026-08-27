"""Tesztek a többkantonos építési engedély federációhoz (ADR-014)."""

from fastapi.testclient import TestClient

from src.main import app


class TestMultiCantonPlanning:
    def test_planning_baugesuche_quick_picks(self) -> None:
        """Mind a 4 Quick-Pick irányítószámhoz (8004, 8001, 3011, 4001, 1201) elérhetők aktív építkezések."""
        client = TestClient(app)
        for pc, expected_canton in [
            ("8004", "ZH"),
            ("8001", "ZH"),
            ("3011", "BE"),
            ("4001", "BS"),
            ("1201", "GE"),
        ]:
            resp = client.get(f"/api/v1/planning/baugesuche?postcode={pc}&active_only=true")
            assert resp.status_code == 200, f"Hiba a {pc} lekérésekor: {resp.status_code}"
            data = resp.json()
            items = data.get("items", [])
            assert len(items) > 0, f"Nincs Baugesuch a {pc} irányítószámhoz!"
            for item in items:
                assert item["canton"] == expected_canton
                assert item["postcode"] == pc
                assert item["lat"] is not None
                assert item["lon"] is not None
                assert item["auflage_end"] is not None
