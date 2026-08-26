import pytest

from src.services.geo_converter import is_valid_lv95, lv95_to_wgs84

ZH_HB_EASTING = 2683100.0
ZH_HB_NORTHING = 1248100.0
ZH_HB_LAT = 47.3781
ZH_HB_LON = 8.5401


def test_coordinate_math_formulas() -> None:
    """Swisstopo approximate formula: ZH HB LV95 -> WGS84 within 0.005°."""
    lat, lon = lv95_to_wgs84(ZH_HB_EASTING, ZH_HB_NORTHING)
    assert abs(lat - ZH_HB_LAT) < 0.005, f"Latitude {lat} deviated from {ZH_HB_LAT}"
    assert abs(lon - ZH_HB_LON) < 0.005, f"Longitude {lon} deviated from {ZH_HB_LON}"


def test_swiss_bounds_rejects_outside_switzerland() -> None:
    """is_valid_lv95 and lv95_to_wgs84 must reject coordinates outside Swiss LV95 bounds."""
    # Valid point must not raise
    lv95_to_wgs84(2_600_000.0, 1_200_000.0)

    # Easting outside bounds
    assert not is_valid_lv95(1_500_000.0, 1_200_000.0)
    with pytest.raises(ValueError, match="easting"):
        lv95_to_wgs84(1_500_000.0, 1_200_000.0)

    # Northing outside bounds
    assert not is_valid_lv95(2_600_000.0, 900_000.0)
    with pytest.raises(ValueError, match="northing"):
        lv95_to_wgs84(2_600_000.0, 900_000.0)
