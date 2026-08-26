"""Geo domain models — WGS84 / LV95 coordinates and address search result.

Pydantic BaseModel, frozen/immutable where appropriate.
Bounds follow Swisstopo LV95 and Swiss WGS84 envelope.
"""

from __future__ import annotations

from typing import Annotated

from pydantic import BaseModel, ConfigDict, Field

# Swiss WGS84 envelope (conservative, covers all of Switzerland)
WGS84_LAT_MIN: float = 45.0
WGS84_LAT_MAX: float = 48.0
WGS84_LON_MIN: float = 5.5
WGS84_LON_MAX: float = 10.6

# LV95 bounds — identical to src.services.geo_converter
LV95_EASTING_MIN: float = 2_400_000.0
LV95_EASTING_MAX: float = 2_900_000.0
LV95_NORTHING_MIN: float = 1_050_000.0
LV95_NORTHING_MAX: float = 1_350_000.0


class CoordinateWGS84(BaseModel):
    """WGS84 coordinate (EPSG:4326) constrained to Swiss envelope."""

    model_config = ConfigDict(frozen=True, strict=True)

    latitude: Annotated[float, Field(ge=WGS84_LAT_MIN, le=WGS84_LAT_MAX)]
    longitude: Annotated[float, Field(ge=WGS84_LON_MIN, le=WGS84_LON_MAX)]


class CoordinateLV95(BaseModel):
    """LV95 coordinate (EPSG:2056) from Swisstopo."""

    model_config = ConfigDict(frozen=True, strict=True)

    easting: Annotated[float, Field(ge=LV95_EASTING_MIN, le=LV95_EASTING_MAX)]
    northing: Annotated[float, Field(ge=LV95_NORTHING_MIN, le=LV95_NORTHING_MAX)]

    def to_wgs84(self) -> CoordinateWGS84:
        """Convert this LV95 point to WGS84 using Swisstopo approximate formula."""
        y_aux = (self.easting - 2_600_000.0) / 1_000_000.0
        x_aux = (self.northing - 1_200_000.0) / 1_000_000.0

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

        return CoordinateWGS84(latitude=lat, longitude=lon)


class AddressSearchResult(BaseModel):
    """Single geocoder hit (Swisstopo SearchServer / Nominatim-style).

    `label` is the human display string, coordinates are WGS84.
    Optional structured address parts mirror Swisstopo `attrs` response.
    """

    model_config = ConfigDict(frozen=True, strict=True)

    label: Annotated[str, Field(min_length=1)]
    latitude: Annotated[float, Field(ge=WGS84_LAT_MIN, le=WGS84_LAT_MAX)]
    longitude: Annotated[float, Field(ge=WGS84_LON_MIN, le=WGS84_LON_MAX)]
    canton: Annotated[str, Field(min_length=2, max_length=2)] | None = None
    municipality: str | None = None
    postal_code: Annotated[str, Field(min_length=4, max_length=4)] | None = None
    street: str | None = None
    house_number: str | None = None
    score: Annotated[float, Field(ge=0.0, le=1.0)] | None = None
