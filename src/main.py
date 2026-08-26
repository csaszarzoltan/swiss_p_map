"""FastAPI app — Swiss P Map API v1."""

from __future__ import annotations

import os

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware

from src.models.geo import CoordinateWGS84
from src.services.geo_converter import lv95_to_wgs84
from src.services.place_service import PlaceService
from src.services.planning_service import PlanningService
from src.services.politics_service import PoliticsService

_DEFAULT_CORS_ORIGINS = "http://localhost:3000"


def _allowed_origins() -> list[str]:
    """Engedélyezett CORS originek — `SWISSPM_CORS_ORIGINS` (vesszővel tagolt) felülírhatja."""
    raw = os.environ.get("SWISSPM_CORS_ORIGINS", "").strip()
    if not raw:
        return [_DEFAULT_CORS_ORIGINS]
    return [item.strip() for item in raw.split(",") if item.strip()]


app = FastAPI(title="Swiss P Map", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=_allowed_origins(),
    allow_methods=["*"],
    allow_headers=["*"],
)

_politics = PoliticsService()
_place = PlaceService()
_planning = PlanningService()


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok", "app": "swiss-p-map", "version": "0.1.0"}


@app.get("/api/v1/geo/convert")
def geo_convert(
    easting: float = Query(..., description="LV95 easting"),
    northing: float = Query(..., description="LV95 northing"),
) -> dict[str, object]:
    try:
        lat, lon = lv95_to_wgs84(easting, northing)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    wgs = CoordinateWGS84(latitude=lat, longitude=lon)
    return {"wgs84": wgs.model_dump(), "lv95": {"easting": easting, "northing": northing}}


@app.get("/api/v1/politics/representatives")
def politics_representatives(postcode: str = Query(..., min_length=4, max_length=4)) -> dict[str, object]:
    data = _politics.get_by_postcode(postcode)
    if data is None:
        raise HTTPException(status_code=404, detail=f"no data for postcode {postcode}")
    return data.model_dump()


@app.get("/api/v1/place/{postcode}")
def place_info(postcode: str) -> dict[str, object]:
    data = _place.get_by_postcode(postcode)
    if data is None:
        raise HTTPException(status_code=404, detail=f"no data for postcode {postcode}")
    return data.model_dump()


@app.get("/api/v1/planning/baugesuche")
def planning_baugesuche(
    postcode: str | None = Query(default=None, min_length=4, max_length=4),
    active_only: bool = Query(default=True),
) -> dict[str, object]:
    items = _planning.list_items(postcode=postcode, active_only=active_only)
    return {"items": [b.model_dump(mode="json") for b in items]}
