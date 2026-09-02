"""FastAPI app — Swiss P Map API v1."""

from __future__ import annotations

import os

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware

from src.models.geo import CoordinateWGS84
from src.services.ai_summary_service import AiSummaryService
from src.services.air_quality_service import AirQualityService
from src.services.building_energy_service import BuildingEnergyService
from src.services.connectivity_service import ConnectivityService
from src.services.education_service import EducationService
from src.services.geo_converter import lv95_to_wgs84
from src.services.hazard_service import HazardService
from src.services.healthcare_service import HealthcareService
from src.services.isos_service import IsosService
from src.services.microclimate_service import MicroclimateService
from src.services.place_service import PlaceService
from src.services.planning_service import PlanningService
from src.services.politics_service import PoliticsService
from src.services.property_price_service import PropertyPriceService
from src.services.tax_service import TaxService
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
_microclimate = MicroclimateService()
_education = EducationService()
_building_energy = BuildingEnergyService()
_air_quality = AirQualityService()
_healthcare = HealthcareService()
_connectivity = ConnectivityService()
_vote = VoteService()
_property_prices = PropertyPriceService()
_tax = TaxService()
_hazard = HazardService()
_isos = IsosService()
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
                title="Badenerstrasse 120, 8004 Zürich — Dachausbau & Aufstockung (Amtsblatt ZH)",
                municipality="Zürich",
                municipality_id=261,
                postcode="8004",
                canton="ZH",
                publication_date=_today - _td(days=5),
                expiration_date=_today + _td(days=360),
                auflage_start=_today - _td(days=5),
                auflage_end=_today + _td(days=15),
                source_url="https://amtsblattportal.ch/api/v1/publications/demo-8004-1/xml",
                geocode_precision="address",
                lat=47.374,
                lon=8.525,
                contractor="Immo Zürich AG",
                architect="EM2N Architekten ETH SIA",
                parcel_number="Kat.-Nr. 4812 / Assek. 1044",
                zone_type="Kernzone (K)",
                risk_level="high",
            ),
            _BG(
                id="demo-8004-2",
                title="Hohlstrasse 216, 8004 Zürich — Gewerbeumbau & PV-Anlage (Amtsblatt ZH)",
                municipality="Zürich",
                municipality_id=261,
                postcode="8004",
                canton="ZH",
                publication_date=_today - _td(days=10),
                expiration_date=_today + _td(days=355),
                auflage_start=_today - _td(days=10),
                auflage_end=_today + _td(days=10),
                source_url="https://amtsblattportal.ch/api/v1/publications/demo-8004-2/xml",
                geocode_precision="address",
                lat=47.382,
                lon=8.515,
                contractor="Swisscom Immobilien AG",
                architect="Gigon/Guyer Architekten",
                parcel_number="Kat.-Nr. 5120",
                zone_type="Industrie- und Gewerbezone",
                risk_level="medium",
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
                contractor="ETH Zürich Bauten",
                architect="Boltshauser Architekten",
                parcel_number="Kat.-Nr. 1010",
                zone_type="Zone für öffentliche Bauten",
                risk_level="low",
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
                contractor="Wohnbaugenossenschaft Uster",
                architect="Meier Partner AG",
                parcel_number="Assek. Nr. 7325",
                zone_type="Wohnzone W3",
                risk_level="medium",
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
                contractor="Burgergemeinde Bern",
                architect="Atelier 5 Architekten",
                parcel_number="Grundbuch Bern 124",
                zone_type="UNESCO Altstadtzone (A)",
                risk_level="high",
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
                contractor="PSP Swiss Property AG",
                architect="Kämpfen Zinke Partner",
                parcel_number="Grundbuch Bern 890",
                zone_type="Geschäftszone Zentrum",
                risk_level="medium",
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
                contractor="Basler Kantonalbank Immobilien",
                architect="Herzog & de Meuron",
                parcel_number="Sektion 1 / Parz. 402",
                zone_type="Schonzone Altstadt",
                risk_level="low",
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
                contractor="Genève Patrimoine Foncière SA",
                architect="Bonnard Woeffray Architectes",
                parcel_number="Feuille 12 / N° 3401",
                zone_type="Zone de développement 2",
                risk_level="high",
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


@app.get("/api/v1/politics/votes/list")
def politics_votes_list() -> dict[str, object]:
    """Elérhető szövetségi népszavazási javaslatok listája (ADR-017)."""
    return {"items": _vote.list_proposals()}


@app.get("/api/v1/politics/votes/{proposal_id}")
def politics_vote_by_id(proposal_id: int) -> dict[str, object]:
    """Egy konkrét szövetségi javaslat 26 kantonos adatai (ADR-017)."""
    item = _vote.get_proposal_by_id(proposal_id)
    if item is None:
        raise HTTPException(status_code=404, detail=f"Proposal {proposal_id} not found")
    return item.model_dump()


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


@app.get("/api/v1/planning/radius")
def planning_radius(
    lat: float = Query(..., ge=45.0, le=48.0, description="WGS84 latitude"),
    lon: float = Query(..., ge=5.0, le=11.0, description="WGS84 longitude"),
    radius_m: float = Query(default=1000.0, ge=50.0, le=50000.0, description="Search radius in meters"),
    active_only: bool = Query(default=True),
) -> dict[str, object]:
    """Térbeli sugárkeresés adott koordináta körül méterben (ADR-018)."""
    items_with_dist = _planning.find_by_radius(lat=lat, lon=lon, radius_m=radius_m, active_only=active_only)
    return {
        "count": len(items_with_dist),
        "radius_m": radius_m,
        "items": [
            {**b.model_dump(mode="json"), "distance_m": round(dist, 1)}
            for b, dist in items_with_dist
        ],
    }


@app.get("/api/v1/planning/bbox")
def planning_bbox(
    min_lat: float = Query(..., ge=45.0, le=48.0),
    min_lon: float = Query(..., ge=5.0, le=11.0),
    max_lat: float = Query(..., ge=45.0, le=48.0),
    max_lon: float = Query(..., ge=5.0, le=11.0),
    active_only: bool = Query(default=True),
) -> dict[str, object]:
    """Térképnézeti befoglaló téglalap lekérdezés (ADR-018)."""
    items = _planning.find_by_bbox(
        min_lat=min_lat, min_lon=min_lon, max_lat=max_lat, max_lon=max_lon, active_only=active_only
    )
    return {"count": len(items), "items": [b.model_dump(mode="json") for b in items]}


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


@app.get("/api/v1/property/prices")
def property_prices(
    canton: str = Query(..., min_length=2, max_length=2, pattern=r"^[A-Za-z]{2}$"),
    postcode: str = Query(..., min_length=4, max_length=4, pattern=r"^\d{4}$"),
) -> dict[str, object]:
    """SPEC-034 REQ-001..005: source-labelled BFS IMPI regional trends."""
    return _property_prices.get_assessment(canton, postcode).model_dump()


@app.get("/api/v1/tax/comparison")
def tax_comparison(
    canton: str = Query(..., min_length=2, max_length=2, pattern=r"^[A-Za-z]{2}$"),
) -> dict[str, object]:
    """SPEC-032 REQ-001..005: 26-canton tax ranking and neighbors."""
    result = _tax.compare(canton)
    if result is None:
        raise HTTPException(status_code=404, detail=f"unknown canton {canton.upper()}")
    return result.model_dump()


@app.get("/api/v1/hazard/assessment")
def hazard_assessment(
    postcode: str = Query(..., min_length=4, max_length=4, pattern=r"^\d{4}$"),
    lat: float = Query(..., ge=45.0, le=48.0),
    lon: float = Query(..., ge=5.0, le=11.0),
) -> dict[str, object]:
    """SPEC-035 REQ-001..005: indicative BAFU hazard screening."""
    return _hazard.assess(postcode, lat, lon).model_dump()


@app.get("/api/v1/heritage/isos")
def heritage_isos(
    postcode: str = Query(..., min_length=4, max_length=4, pattern=r"^\d{4}$"),
) -> dict[str, object]:
    """SPEC-036 REQ-001..005: ISOS I/II federal inventory screening."""
    return _isos.assess(postcode).model_dump()


@app.get("/api/v1/climate/microclimate")
def climate_microclimate(postcode: str = Query(..., pattern=r"^\d{4}$"), canton: str = Query(..., pattern=r"^[A-Za-z]{2}$")) -> dict[str, object]:
    """SPEC-037 REQ-001 AC-001."""
    return _microclimate.assess(postcode, canton).model_dump()


@app.get("/api/v1/education/facilities")
def education_facilities(postcode: str = Query(..., pattern=r"^\d{4}$")) -> dict[str, object]:
    """SPEC-038 REQ-001 AC-001."""
    return _education.facilities(postcode).model_dump()


@app.get("/api/v1/energy/assessment")
def energy_assessment(postcode: str = Query(..., pattern=r"^\d{4}$")) -> dict[str, object]:
    """SPEC-043 REQ-001 AC-001."""
    return _building_energy.assess(postcode).model_dump()


@app.get("/api/v1/environment/air-pollen")
def environment_air_pollen(postcode: str = Query(..., pattern=r"^\d{4}$")) -> dict[str, object]:
    """SPEC-040 REQ-001 AC-001."""
    return _air_quality.assess(postcode).model_dump()


@app.get("/api/v1/healthcare/access")
def healthcare_access(postcode: str = Query(..., pattern=r"^\d{4}$")) -> dict[str, object]:
    """SPEC-041 REQ-001 AC-001."""
    return _healthcare.access(postcode).model_dump()


@app.get("/api/v1/connectivity/status")
def connectivity_status(postcode: str = Query(..., pattern=r"^\d{4}$")) -> dict[str, object]:
    """SPEC-042 REQ-001 AC-001."""
    return _connectivity.status(postcode).model_dump()
