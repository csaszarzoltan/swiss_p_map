"""Unit tests for Spatial Radius and BBox Planning queries (ADR-018)."""

from fastapi.testclient import TestClient

from src.main import app
from src.services.geo_converter import haversine_distance_m


class TestPlanningSpatial:
    def test_haversine_distance_accuracy(self) -> None:
        """Haversine távolság pontosság ellenőrzése: Zürich HB -> Helvetiaplatz ~1.2 km."""
        # Zurich HB: 47.378, 8.540; Helvetiaplatz: 47.373, 8.526
        d = haversine_distance_m(47.378, 8.540, 47.373, 8.526)
        assert 1000.0 < d < 1400.0, f"Váratlan távolság: {d}m"

    def test_planning_radius_search_returns_sorted_items(self) -> None:
        """A /api/v1/planning/radius végpont távolság szerint növekvő listát ad."""
        client = TestClient(app)
        # Search around Zürich Aussersihl 8004 (47.388, 8.523) with 2000m radius
        resp = client.get("/api/v1/planning/radius?lat=47.388&lon=8.523&radius_m=2000&active_only=false")
        assert resp.status_code == 200
        data = resp.json()
        assert data["count"] > 0
        items = data["items"]
        assert len(items) > 0

        # Verify distance_m exists and is strictly non-decreasing
        distances = [item["distance_m"] for item in items]
        assert distances == sorted(distances)
        assert all(d <= 2000.0 for d in distances)

    def test_planning_bbox_search_within_bounds(self) -> None:
        """A /api/v1/planning/bbox végpont csak a téglalapba eső projekteket adja."""
        client = TestClient(app)
        # Search bounding box around Bern (lat ~46.94..46.96, lon ~7.43..7.46)
        resp = client.get("/api/v1/planning/bbox?min_lat=46.94&max_lat=46.96&min_lon=7.43&max_lon=7.46&active_only=false")
        assert resp.status_code == 200
        data = resp.json()
        assert data["count"] > 0
        for item in data["items"]:
            assert 46.94 <= item["lat"] <= 46.96
            assert 7.43 <= item["lon"] <= 7.46
