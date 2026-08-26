"""Swisstopo LV95 ↔ WGS84 coordinate converter.

Uses the official Swisstopo approximate formulas for tests / offline use.
Production code should prefer PyProj (EPSG:2056 ↔ EPSG:4326) where available.
"""

from __future__ import annotations

# LV95 valid bounds (conservative, per swisstopo)
EASTING_MIN = 2_400_000.0
EASTING_MAX = 2_900_000.0
NORTHING_MIN = 1_050_000.0
NORTHING_MAX = 1_350_000.0


def lv95_to_wgs84(easting: float, northing: float) -> tuple[float, float]:
    """Convert LV95 (EPSG:2056) to WGS84 (EPSG:4326).

    Returns (latitude, longitude) in decimal degrees.
    Raises ValueError if coordinates are outside valid Swiss bounds.
    """
    if not (EASTING_MIN <= easting <= EASTING_MAX):
        raise ValueError(f"easting {easting} outside LV95 bounds [{EASTING_MIN}, {EASTING_MAX}]")
    if not (NORTHING_MIN <= northing <= NORTHING_MAX):
        raise ValueError(f"northing {northing} outside LV95 bounds [{NORTHING_MIN}, {NORTHING_MAX}]")

    y_aux = (easting - 2_600_000.0) / 1_000_000.0
    x_aux = (northing - 1_200_000.0) / 1_000_000.0

    lat = (
        16.9023892
        + 3.238272 * x_aux
        - 0.270978 * (y_aux**2)
        - 0.002528 * (x_aux**2)
        - 0.0447 * (y_aux**2) * x_aux
        - 0.0140 * (x_aux**3)
    ) * (100.0 / 36.0)

    lon = (
        2.6779094
        + 4.728982 * y_aux
        + 0.791484 * y_aux * x_aux
        + 0.1306 * y_aux * (x_aux**2)
        - 0.0436 * (y_aux**3)
    ) * (100.0 / 36.0)

    return lat, lon


def is_valid_lv95(easting: float, northing: float) -> bool:
    """Return True if the LV95 coordinate is within valid Swiss bounds."""
    return (EASTING_MIN <= easting <= EASTING_MAX) and (NORTHING_MIN <= northing <= NORTHING_MAX)
