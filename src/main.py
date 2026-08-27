"""FastAPI app — Swiss P Map API v1."""

from __future__ import annotations

import os

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware

from src.models.geo import CoordinateWGS84
from src.services.ai_summary_service import AiSummaryService
from src.services.geo_converter import lv95_to_wgs84
from src.services.place_service import PlaceService
from src.services.planning_service import PlanningService
from src.services.politics_service import PoliticsService
from src.services.vote_service import VoteService

_DEFAULT_CORS_ORIGINS = (
    "http://localhost:3000,http://127.0.0.1:3000,http://localhost:3310,http://127.0.0.1:3310,http://localhost:3410,http://127.0.0.1:3410"
)


def _allowed_origins() -> list[str]:
    """Engedélyezett CORS originek — `SWISSPM_CORS_ORIGINS` (vesszővel tagolt) felülírhatja."""
    raw = os.environ.get("SWISSPM_CORS_ORIGINS", "").strip()
    source = raw if raw else _DEFAULT_CORS_ORIGINS
    return [item.strip() for item in source.split(",") if item.strip()]


app = FastAPI(title="Swiss P Map", version="0.2.1")

app.add_middleware(
    CORSMiddleware,
    allow_origins=_allowed_origins(),
    allow_methods=["*"],
    allow_headers=["*"],
)

_politics = PoliticsService()
_place = PlaceService()
_planning = PlanningService()
_ai = AiSummaryService()
_vote = VoteService()
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
                id="demo-8001-1",
                title="Rämistrasse 101, 8001 Zürich — Sanierung Laborgebäude (Amtsblatt ZH)",
                municipality="Zürich",
                municipality_id=261,
                postcode="8001",
                canton="ZH",
                publication_date=_today - _td(days=3),
                expiration_date=_today + _td(days=362),
                auflage_start=_today - _td(days=3),
                auflage_end=_today + _td(days=17),
                source_url="https://amtsblattportal.ch/api/v1/publications/demo-8001-1/xml",
                geocode_precision="address",
                lat=47.376,
                lon=8.548,
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
            _BG(
                id="demo-3011-1",
                title="Kramgasse 45, 3011 Bern — Sanierung Altstadt-Wohnhaus (Amtsanzeiger Bern)",
                municipality="Bern",
                municipality_id=351,
                postcode="3011",
                canton="BE",
                publication_date=_today - _td(days=4),
                expiration_date=_today + _td(days=361),
                auflage_start=_today - _td(days=4),
                auflage_end=_today + _td(days=16),
                source_url="https://amtsblattportal.ch/api/v1/publications/demo-3011-1/xml",
                geocode_precision="address",
                lat=46.948,
                lon=7.449,
            ),
            _BG(
                id="demo-3011-2",
                title="Spitalgasse 12, 3011 Bern — Umbau Geschäftsräume (eBau BE)",
                municipality="Bern",
                municipality_id=351,
                postcode="3011",
                canton="BE",
                publication_date=_today - _td(days=8),
                expiration_date=_today + _td(days=357),
                auflage_start=_today - _td(days=8),
                auflage_end=_today + _td(days=12),
                source_url="https://amtsblattportal.ch/api/v1/publications/demo-3011-2/xml",
                geocode_precision="address",
                lat=46.947,
                lon=7.444,
            ),
            _BG(
                id="demo-4001-1",
                title="Freie Strasse 25, 4001 Basel — Fassadenrenovation & PV (Kantonsblatt BS)",
                municipality="Basel",
                municipality_id=2701,
                postcode="4001",
                canton="BS",
                publication_date=_today - _td(days=6),
                expiration_date=_today + _td(days=359),
                auflage_start=_today - _td(days=6),
                auflage_end=_today + _td(days=14),
                source_url="https://amtsblattportal.ch/api/v1/publications/demo-4001-1/xml",
                geocode_precision="address",
                lat=47.556,
                lon=7.591,
            ),
            _BG(
                id="demo-1201-1",
                title="Rue du Mont-Blanc 14, 1201 Genève — Surélévation d'immeuble (FAO GE)",
                municipality="Genève",
                municipality_id=6621,
                postcode="1201",
                canton="GE",
                publication_date=_today - _td(days=7),
                expiration_date=_today + _td(days=358),
                auflage_start=_today - _td(days=7),
                auflage_end=_today + _td(days=13),
                source_url="https://amtsblattportal.ch/api/v1/publications/demo-1201-1/xml",
                geocode_precision="address",
                lat=46.210,
                lon=6.146,
            ),
        ]
    )
except Exception:  # noqa: BLE001,S110 — demo seed nem törheti az app indulását
    pass


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok", "app": "swiss-p-map", "version": "0.2.1"}


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
async def politics_representatives(
    postcode: str = Query(..., min_length=4, max_length=4),
    live: bool = Query(default=False, description="Ha true, PARIS CQL élő lekérés (ADR-005); fallback stub"),
) -> dict[str, object]:
    if live:
        data = await _politics.get_by_postcode_live(postcode)
        if data is not None:
            return data.model_dump()
    data = _politics.get_by_postcode(postcode)
    if data is None:
        raise HTTPException(status_code=404, detail=f"no data for postcode {postcode}")
    return data.model_dump()


@app.get("/api/v1/politics/votes/latest")
def politics_votes_latest() -> dict[str, object]:
    """Hivatalos szövetségi népszavazási eredmények kantonális bontásban (ADR-012)."""
    return _vote.get_latest_vote().model_dump()


@app.get("/api/v1/place/{postcode}")
async def place_info(
    postcode: str,
    live: bool = Query(default=False, description="Ha true, api3 Identify élő (ARE/BAFU) + fallback stub (ADR-005)"),
) -> dict[str, object]:
    if live:
        data = await _place.get_by_postcode_live(postcode)
        if data is not None:
            return data.model_dump()
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


@app.post("/api/v1/planning/refresh")
async def planning_refresh(payload: dict[str, object] | None = None) -> dict[str, object]:
    canton = str((payload or {}).get("canton") or "ZH")
    try:
        count = await _planning.refresh(canton=canton)
    except Exception as exc:
        raise HTTPException(status_code=502, detail=f"refresh_failed: {exc}") from exc
    return {"count": count, "refreshed": count}


@app.post("/api/v1/planning/backfill")
async def planning_backfill(payload: dict[str, object] | None = None) -> dict[str, object]:
    _ = payload  # future: source filter
    try:
        count = await _planning.backfill_ogd()
    except Exception as exc:
        raise HTTPException(status_code=502, detail=f"backfill_failed: {exc}") from exc
    return {"count": count, "source": "ogd"}


@app.post("/api/v1/ai/summary")
async def ai_summary(payload: dict[str, object]) -> dict[str, str]:
    locale = str(payload.get("locale") or "de")
    postcode = str(payload.get("postcode") or "")
    place = payload.get("place") if isinstance(payload.get("place"), dict) else {}
    politics = payload.get("politics") if isinstance(payload.get("politics"), dict) else {}
    baugesuche = payload.get("baugesuche") if isinstance(payload.get("baugesuche"), list) else []
    summary = await _ai.summarize(locale, postcode, place, politics, baugesuche)  # type: ignore[arg-type]
    if summary is None:
        raise HTTPException(status_code=502, detail="ai_unavailable")
    return {"summary": summary}
