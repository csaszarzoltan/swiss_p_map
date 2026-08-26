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
# Demo seed — amíg nincs napi Amtsblatt poll, 8004-en legyen aktív Baugesuch a bemutatóhoz
try:
    from datetime import date as _d
    from datetime import timedelta as _td

    from src.models.planning import Baugesuch as _BG

    _today = _d.today()  # noqa: DTZ011 — demo seed wall-clock, SQLite task majd injectált "on"
    _planning.seed(
        [
            _BG(
                id="demo-8004-1",
                title="Umbau Mehrfamilienhaus — Badenerstrasse 100, 8004 Zürich",
                municipality="Zürich",
                municipality_id=261,
                postcode="8004",
                canton="ZH",
                publication_date=_today - _td(days=5),
                expiration_date=_today + _td(days=360),
                auflage_start=_today - _td(days=5),
                auflage_end=_today + _td(days=15),
                source_url="https://amtsblattportal.ch/api/v1/publications/demo-8004-1/xml",
                geocode_precision="locality",
                lat=47.392,
                lon=8.517,
            ),
            _BG(
                id="demo-8004-2",
                title="Neubau Wohnüberbauung — Hardstrasse 12, 8004 Zürich",
                municipality="Zürich",
                municipality_id=261,
                postcode="8004",
                canton="ZH",
                publication_date=_today - _td(days=12),
                expiration_date=_today + _td(days=353),
                auflage_start=_today - _td(days=12),
                auflage_end=_today + _td(days=8),
                source_url="https://amtsblattportal.ch/api/v1/publications/demo-8004-2/xml",
                geocode_precision="address",
                lat=47.388,
                lon=8.523,
            ),
            _BG(
                id="demo-8610-1",
                title="Seefeldstrasse 6, Assek. Nr. 7325, 8610 Uster — Neubau (Demo)",
                municipality="Uster",
                municipality_id=198,
                postcode="8610",
                canton="ZH",
                publication_date=_today - _td(days=2),
                expiration_date=_today + _td(days=363),
                auflage_start=_today - _td(days=2),
                auflage_end=_today + _td(days=18),
                source_url="https://amtsblattportal.ch/api/v1/publications/demo-8610-1/xml",
                geocode_precision="address",
                lat=47.35,
                lon=8.72,
            ),
        ]
    )
except Exception:  # noqa: BLE001,S110 — demo seed nem törheti az app indulását
    pass


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
