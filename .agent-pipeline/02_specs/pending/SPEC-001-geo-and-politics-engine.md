# SPEC-001: Swiss Geodata Coordinate Converter & Politics Service (Zürich Pilot)

## Target Files
- `src/models/geo.py` (NEW: Coordinate & Geocoding Pydantic models)
- `src/models/politics.py` (NEW: Representative & Vorstoss Pydantic models)
- `src/services/geo_converter.py` (NEW: LV95 / EPSG:2056 <-> WGS84 / EPSG:4326 converter)
- `src/services/swisstopo_service.py` (NEW: Swisstopo geocoding search service)
- `src/services/politics_service.py` (NEW: Stadt Zürich Wahlkreis & PARIS-API connector)
- `src/main.py` (NEW: FastAPI app routing)
- `tests/unit/test_geo_converter.py` (NEW: Unit tests for coordinate math)
- `tests/unit/test_swisstopo_service.py` (NEW: Unit tests for Swisstopo geocoder)
- `tests/unit/test_politics_service.py` (NEW: Unit tests for representative lookup)

## Python Interface Definitions

```python
from __future__ import annotations
from pydantic import BaseModel, Field
from enum import Enum
from typing import List, Optional

class CoordinateWGS84(BaseModel):
    latitude: float = Field(..., ge=-90.0, le=90.0, description="WGS84 Latitude")
    longitude: float = Field(..., ge=-180.0, le=180.0, description="WGS84 Longitude")

class CoordinateLV95(BaseModel):
    easting: float = Field(..., ge=2400000.0, le=2900000.0, description="Swiss Easting (E / Y)")
    northing: float = Field(..., ge=1050000.0, le=1350000.0, description="Swiss Northing (N / X)")

class AddressSearchResult(BaseModel):
    label: str
    wgs84: CoordinateWGS84
    lv95: CoordinateLV95
    canton: str
    municipality: str
    postcode: Optional[str] = None

class PoliticalParty(str, Enum):
    SP = "SP"
    FDP = "FDP"
    SVP = "SVP"
    GRUENE = "Grüne"
    GLP = "GLP"
    MITTE = "Die Mitte"
    AL = "AL"
    EVP = "EVP"
    OTHER = "Other"

class ParliamentaryProposal(BaseModel):
    id: str
    title: str
    type: str  # e.g., "Motion", "Postulat", "Interpellation"
    status: str  # e.g., "Eingereicht", "Überwiesen", "Abgeschlossen"
    submitted_date: str
    topic_category: str

class Representative(BaseModel):
    id: str
    name: str
    party: PoliticalParty
    council_level: str  # "Gemeinderat", "Kantonsrat", "Nationalrat"
    electoral_district: str  # e.g., "Wahlkreis 4+5 (Aussersihl-Industrie)"
    occupation: Optional[str] = None
    email: Optional[str] = None
    website: Optional[str] = None
    proposals: List[ParliamentaryProposal] = Field(default_factory=list)

class DistrictRepresentativesResponse(BaseModel):
    district_name: str
    canton: str
    representatives_count: int
    representatives: List[Representative]
```

## Step-by-Step Implementation Details

1. **`src/services/geo_converter.py`:**
   - Implement `lv95_to_wgs84(easting: float, northing: float) -> CoordinateWGS84` using standard Swisstopo approximate formulas (or `pyproj` with fallback):
     - $y' = (E - 2600000) / 1000000$
     - $x' = (N - 1200000) / 1000000$
     - Compute longitude $\lambda$ and latitude $\varphi$ in decimal degrees.
   - Implement `wgs84_to_lv95(latitude: float, longitude: float) -> CoordinateLV95`.
   - Validate bounds: if coordinates fall outside Switzerland, raise `ValueError("Coordinates out of Swiss bounds")`.

2. **`src/services/swisstopo_service.py`:**
   - Implement `SwisstopoService.search_address(query: str) -> List[AddressSearchResult]`.
   - Query `https://api3.geo.admin.ch/rest/services/api/SearchServer?type=locations&searchText={query}` via `httpx.AsyncClient`.
   - Parse GeoJSON/JSON features, extract coordinates, convert to both LV95 and WGS84.

3. **`src/services/politics_service.py`:**
   - Map Zürich postal codes (e.g. `8004`, `8005`) to City Council Electoral Districts (*Wahlkreise 1–12*).
   - Implement `PoliticsService.get_representatives_by_district(district_id: str) -> DistrictRepresentativesResponse`.
   - Provide integration with Stadt Zürich PARIS-API with local fallback fixtures for offline resilience.

4. **`src/main.py`:**
   - Set up FastAPI app with CORS middleware and routes:
     - `GET /health` $\rightarrow$ `{"status": "ok", "app": "swiss-p-map", "version": "0.1.0"}`
     - `GET /api/v1/geo/convert` $\rightarrow$ Accepts WGS84 or LV95, returns converted coordinates.
     - `GET /api/v1/geo/search?q={query}` $\rightarrow$ Returns list of `AddressSearchResult`.
     - `GET /api/v1/politics/representatives?postcode={postcode}` $\rightarrow$ Returns `DistrictRepresentativesResponse`.

## Unit Test Acceptance Criteria (`pytest`)

* `test_lv95_to_wgs84_zurich_hb`: Known point (E: 2683100, N: 1248100) converts within $\pm 0.0001^{\circ}$ of $(47.3781, 8.5401)$.
* `test_wgs84_to_lv95_bern_bundeshaus`: Known point $(46.9465, 7.4442)$ converts to within $\pm 1.0\text{ m}$ of $(2600400, 1199700)$.
* `test_out_of_bounds_coordinate_raises_value_error`: Coordinates outside Swiss borders raise `ValueError`.
* `test_swisstopo_search_address_mocked`: Mocked response returns normalized `AddressSearchResult` list.
* `test_politics_service_zurich_district_4_5`: Querying postcode `8004` returns `Wahlkreis 4+5` representatives.
