"""Unit tests for geo & place domain models — TDD RED phase.

Covers src/models/geo.py (CoordinateWGS84, CoordinateLV95, AddressSearchResult)
and src/models/place.py (SteuerfussEntry, SonBaseExposure, OeVGueteklasse + mocks).

Run: pytest tests/unit/test_geo_models.py -v
"""

from __future__ import annotations

import pytest
from pydantic import ValidationError

# ---------------------------------------------------------------------------
# geo — CoordinateWGS84
# ---------------------------------------------------------------------------


class TestCoordinateWGS84:
    def test_valid_zurich_hb(self) -> None:
        """Happy: Zürich HB inside Swiss WGS84 bounds."""
        from src.models.geo import CoordinateWGS84

        c = CoordinateWGS84(latitude=47.3781, longitude=8.5401)
        assert c.latitude == pytest.approx(47.3781)
        assert c.longitude == pytest.approx(8.5401)

    def test_valid_border_geneva(self) -> None:
        from src.models.geo import CoordinateWGS84

        c = CoordinateWGS84(latitude=46.2044, longitude=6.1432)
        assert c.latitude == pytest.approx(46.2044)

    def test_rejects_latitude_too_low(self) -> None:
        from src.models.geo import CoordinateWGS84

        with pytest.raises(ValidationError):
            CoordinateWGS84(latitude=40.0, longitude=8.5)

    def test_rejects_latitude_too_high(self) -> None:
        from src.models.geo import CoordinateWGS84

        with pytest.raises(ValidationError):
            CoordinateWGS84(latitude=49.0, longitude=8.5)

    def test_rejects_longitude_too_low(self) -> None:
        from src.models.geo import CoordinateWGS84

        with pytest.raises(ValidationError):
            CoordinateWGS84(latitude=47.0, longitude=4.0)

    def test_rejects_longitude_too_high(self) -> None:
        from src.models.geo import CoordinateWGS84

        with pytest.raises(ValidationError):
            CoordinateWGS84(latitude=47.0, longitude=12.0)

    def test_frozen_immutable(self) -> None:
        from src.models.geo import CoordinateWGS84

        c = CoordinateWGS84(latitude=47.3, longitude=8.5)
        with pytest.raises(Exception):  # noqa: B017
            c.latitude = 48.0

    def test_equality(self) -> None:
        from src.models.geo import CoordinateWGS84

        a = CoordinateWGS84(latitude=47.0, longitude=8.0)
        b = CoordinateWGS84(latitude=47.0, longitude=8.0)
        assert a == b

    def test_model_dump_roundtrip(self) -> None:
        from src.models.geo import CoordinateWGS84

        c = CoordinateWGS84(latitude=47.1, longitude=8.2)
        d = c.model_dump()
        assert d["latitude"] == pytest.approx(47.1)
        assert CoordinateWGS84(**d) == c


# ---------------------------------------------------------------------------
# geo — CoordinateLV95
# ---------------------------------------------------------------------------


class TestCoordinateLV95:
    def test_valid_center_switzerland(self) -> None:
        from src.models.geo import CoordinateLV95

        c = CoordinateLV95(easting=2_600_000.0, northing=1_200_000.0)
        assert c.easting == pytest.approx(2_600_000.0)

    def test_valid_zurich_hb_lv95(self) -> None:
        from src.models.geo import CoordinateLV95

        c = CoordinateLV95(easting=2_683_100.0, northing=1_248_100.0)
        assert c.easting == pytest.approx(2_683_100.0)

    def test_rejects_easting_below_min(self) -> None:
        from src.models.geo import CoordinateLV95

        with pytest.raises(ValidationError, match="easting"):
            CoordinateLV95(easting=2_300_000.0, northing=1_200_000.0)

    def test_rejects_easting_above_max(self) -> None:
        from src.models.geo import CoordinateLV95

        with pytest.raises(ValidationError, match="easting"):
            CoordinateLV95(easting=3_000_000.0, northing=1_200_000.0)

    def test_rejects_northing_below_min(self) -> None:
        from src.models.geo import CoordinateLV95

        with pytest.raises(ValidationError, match="northing"):
            CoordinateLV95(easting=2_600_000.0, northing=1_000_000.0)

    def test_rejects_northing_above_max(self) -> None:
        from src.models.geo import CoordinateLV95

        with pytest.raises(ValidationError, match="northing"):
            CoordinateLV95(easting=2_600_000.0, northing=1_400_000.0)

    def test_frozen(self) -> None:
        from src.models.geo import CoordinateLV95

        c = CoordinateLV95(easting=2_600_000.0, northing=1_200_000.0)
        with pytest.raises(Exception):  # noqa: B017
            c.easting = 2_700_000.0

    def test_to_wgs84_conversion_accuracy(self) -> None:
        """LV95 → WGS84 approximation must be within 0.005° of reference."""
        from src.models.geo import CoordinateLV95

        c = CoordinateLV95(easting=2_683_100.0, northing=1_248_100.0)
        wgs = c.to_wgs84()
        assert abs(wgs.latitude - 47.3781) < 0.005
        assert abs(wgs.longitude - 8.5401) < 0.005

    def test_bounds_helpers(self) -> None:
        from src.models.geo import CoordinateLV95

        # at least one of these helpers/properties exists
        c = CoordinateLV95(easting=2_600_000.0, northing=1_200_000.0)
        # to_wgs84 must return CoordinateWGS84 instance
        from src.models.geo import CoordinateWGS84

        assert isinstance(c.to_wgs84(), CoordinateWGS84)


# ---------------------------------------------------------------------------
# geo — AddressSearchResult
# ---------------------------------------------------------------------------


class TestAddressSearchResult:
    def test_valid_minimal(self) -> None:
        from src.models.geo import AddressSearchResult

        r = AddressSearchResult(
            label="Bahnhofstrasse 1, 8001 Zürich",
            latitude=47.3769,
            longitude=8.5401,
        )
        assert r.label.startswith("Bahnhofstrasse")
        assert r.score is None or 0 <= r.score <= 1

    def test_valid_full_fields(self) -> None:
        from src.models.geo import AddressSearchResult

        r = AddressSearchResult(
            label="Bahnhofstrasse 1, 8001 Zürich",
            latitude=47.3769,
            longitude=8.5401,
            canton="ZH",
            municipality="Zürich",
            postal_code="8001",
            street="Bahnhofstrasse",
            house_number="1",
            score=0.92,
        )
        assert r.canton == "ZH"
        assert r.postal_code == "8001"
        assert r.score == pytest.approx(0.92)

    def test_rejects_invalid_latitude(self) -> None:
        from src.models.geo import AddressSearchResult

        with pytest.raises(ValidationError):
            AddressSearchResult(label="x", latitude=0.0, longitude=8.5)

    def test_rejects_invalid_longitude(self) -> None:
        from src.models.geo import AddressSearchResult

        with pytest.raises(ValidationError):
            AddressSearchResult(label="x", latitude=47.0, longitude=0.0)

    def test_rejects_score_out_of_range(self) -> None:
        from src.models.geo import AddressSearchResult

        with pytest.raises(ValidationError):
            AddressSearchResult(label="x", latitude=47.0, longitude=8.0, score=1.5)
        with pytest.raises(ValidationError):
            AddressSearchResult(label="x", latitude=47.0, longitude=8.0, score=-0.1)

    def test_label_required_non_empty(self) -> None:
        from src.models.geo import AddressSearchResult

        with pytest.raises(ValidationError):
            AddressSearchResult(label="", latitude=47.0, longitude=8.0)


# ---------------------------------------------------------------------------
# place — Steuerfuss
# ---------------------------------------------------------------------------


class TestSteuerfussEntry:
    def test_valid_zuerich_2024(self) -> None:
        from src.models.place import SteuerfussEntry

        e = SteuerfussEntry(
            municipality="Zürich",
            bfs_number=261,
            canton="ZH",
            year=2024,
            steuerfuss_percent=119.0,
        )
        assert e.steuerfuss_percent == pytest.approx(119.0)

    def test_rejects_negative_steuerfuss(self) -> None:
        from src.models.place import SteuerfussEntry

        with pytest.raises(ValidationError):
            SteuerfussEntry(
                municipality="Zürich", bfs_number=261, canton="ZH", year=2024, steuerfuss_percent=-5
            )

    def test_rejects_excessive_steuerfuss(self) -> None:
        from src.models.place import SteuerfussEntry

        with pytest.raises(ValidationError):
            SteuerfussEntry(
                municipality="Zürich", bfs_number=261, canton="ZH", year=2024, steuerfuss_percent=999
            )

    def test_rejects_invalid_bfs(self) -> None:
        from src.models.place import SteuerfussEntry

        with pytest.raises(ValidationError):
            SteuerfussEntry(
                municipality="Zürich", bfs_number=0, canton="ZH", year=2024, steuerfuss_percent=119
            )

    def test_rejects_invalid_canton(self) -> None:
        from src.models.place import SteuerfussEntry

        with pytest.raises(ValidationError):
            SteuerfussEntry(
                municipality="Zürich", bfs_number=261, canton="ZZZ", year=2024, steuerfuss_percent=119
            )

    def test_rejects_year_out_of_range(self) -> None:
        from src.models.place import SteuerfussEntry

        with pytest.raises(ValidationError):
            SteuerfussEntry(
                municipality="Zürich", bfs_number=261, canton="ZH", year=1990, steuerfuss_percent=119
            )

    def test_mock_returns_valid_entries(self) -> None:
        from src.models.place import SteuerfussEntry, mock_steuerfuss_entries

        entries = mock_steuerfuss_entries()
        assert len(entries) >= 2
        for e in entries:
            assert isinstance(e, SteuerfussEntry)
            # re-validate via model_validate
            SteuerfussEntry.model_validate(e.model_dump())


# ---------------------------------------------------------------------------
# place — sonBASE (noise)
# ---------------------------------------------------------------------------


class TestSonBaseExposure:
    def test_valid_road_exposure(self) -> None:
        from src.models.place import NoiseSource, SonBaseExposure

        e = SonBaseExposure(
            latitude=47.3781,
            longitude=8.5401,
            db_day=65.0,
            db_night=55.0,
            source=NoiseSource.ROAD,
        )
        assert e.db_day == pytest.approx(65.0)

    def test_rejects_db_out_of_range(self) -> None:
        from src.models.place import NoiseSource, SonBaseExposure

        with pytest.raises(ValidationError):
            SonBaseExposure(latitude=47.0, longitude=8.0, db_day=200, db_night=50, source=NoiseSource.ROAD)

    def test_rejects_invalid_latitude(self) -> None:
        from src.models.place import NoiseSource, SonBaseExposure

        with pytest.raises(ValidationError):
            SonBaseExposure(latitude=0.0, longitude=8.0, db_day=60, db_night=50, source=NoiseSource.RAIL)

    def test_source_enum_values(self) -> None:
        from src.models.place import NoiseSource

        assert {s.value for s in NoiseSource} == {"road", "rail", "air"}

    def test_mock_returns_valid(self) -> None:
        from src.models.place import SonBaseExposure, mock_sonbase_entries

        entries = mock_sonbase_entries()
        assert len(entries) >= 1
        for e in entries:
            assert isinstance(e, SonBaseExposure)


# ---------------------------------------------------------------------------
# place — ÖV-Güteklassen
# ---------------------------------------------------------------------------


class TestOeVGueteklasse:
    def test_valid_guteklasse_a(self) -> None:
        from src.models.place import OeVGueteklasse, OeVGueteklasseEntry

        e = OeVGueteklasseEntry(
            latitude=47.3781,
            longitude=8.5401,
            guteklasse=OeVGueteklasse.A,
            stop_name="Zürich HB",
        )
        assert e.guteklasse == OeVGueteklasse.A

    def test_all_guteklasse_values(self) -> None:
        from src.models.place import OeVGueteklasse

        assert {g.value for g in OeVGueteklasse} == {"A", "B", "C", "D", "NONE"}

    def test_rejects_invalid_guteklasse(self) -> None:
        from src.models.place import OeVGueteklasseEntry

        with pytest.raises(ValidationError):
            OeVGueteklasseEntry(latitude=47.0, longitude=8.0, guteklasse="Z")  # type: ignore[arg-type]

    def test_rejects_invalid_coordinate(self) -> None:
        from src.models.place import OeVGueteklasse, OeVGueteklasseEntry

        with pytest.raises(ValidationError):
            OeVGueteklasseEntry(latitude=0.0, longitude=8.0, guteklasse=OeVGueteklasse.B)

    def test_mock_returns_valid(self) -> None:
        from src.models.place import OeVGueteklasseEntry, mock_oev_gueteklasse_entries

        entries = mock_oev_gueteklasse_entries()
        assert len(entries) >= 1
        for e in entries:
            assert isinstance(e, OeVGueteklasseEntry)

    def test_frozen_models(self) -> None:
        from src.models.place import OeVGueteklasse, OeVGueteklasseEntry

        e = OeVGueteklasseEntry(latitude=47.0, longitude=8.0, guteklasse=OeVGueteklasse.C)
        with pytest.raises(Exception):  # noqa: B017
            e.guteklasse = OeVGueteklasse.A
