"""Geo domain models — LV95 ↔ WGS84, address search."""

from __future__ import annotations

from pydantic import BaseModel, Field


class CoordinateWGS84(BaseModel):
    """WGS84 coordinate (EPSG:4326)."""

    latitude: float = Field(..., ge=-90.0, le=90.0, description="WGS84 latitude")
    longitude: float = Field(..., ge=-180.0, le=180.0, description="WGS84 longitude")


class CoordinateLV95(BaseModel):
    """Swiss LV95 coordinate (EPSG:2056)."""

    easting: float = Field(
        ..., ge=2_400_000.0, le=2_900_000.0, description="LV95 easting (E)"
    )
    northing: float = Field(
        ..., ge=1_050_000.0, le=1_350_000.0, description="LV95 northing (N)"
    )


class AddressSearchResult(BaseModel):
    """Result of a Swisstopo address/geocoding search."""

    label: str
    wgs84: CoordinateWGS84
    lv95: CoordinateLV95
    canton: str
    municipality: str
    postcode: str | None = None
