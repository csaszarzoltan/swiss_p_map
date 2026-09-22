"""SPEC-047/058: Amtsblatt news pipeline live wiring (TDD).

Traceability:
- REQ-047-001 -> AC-047-001 -> typed get_local + API contract
- REQ-047-002 -> AC-047-001 -> source/trust/fetched_at on every item
- REQ-047-004 -> AC-047-002 -> empty store is honest source_pending, never fabricated
- REQ-058-001 -> AC-058-001 -> real XML ingest counts + API contract
- REQ-058-002 -> AC-058-001 -> ingest carries source/trust/fetched_at
- REQ-058-004 -> AC-058-003 -> no fake live data on provider failure
- REQ-058-005 -> AC-058-002 -> failure fallback is source_pending, never official
- REQ-058-006 -> AC-058-003 -> idempotent re-ingest (deduplicated success)
"""

from __future__ import annotations

from datetime import UTC, datetime, timedelta
from unittest.mock import AsyncMock, MagicMock

import httpx
from fastapi.testclient import TestClient

import src.main as main_mod
from src.db.planning_repo import PlanningRepo
from src.main import app
from src.services.amtsblatt_service import AmtsblattService
from src.services.connectors.amtsblatt_news_pipeline import AmtsblattNewsPipeline
from src.services.local_news_service import LocalNewsService

# Fixture dates stay inside the Auflage window (+20d legal window, ADR-002):
# pub = today-5d -> active until today+15d regardless of wall-clock drift.
_today = datetime.now(UTC).date()
_PUB = (_today - timedelta(days=5)).isoformat()
_EXP = (_today + timedelta(days=360)).isoformat()

SAMPLE_XML_TWO = f"""<?xml version="1.0" encoding="UTF-8"?>
<result xmlns:ns2="http://amtsblattportal.ch/schemas/kabzh/1.26/BP-ZH01-export.xsd">
  <total>2</total>
  <publications>
    <publication>
      <id>c1f797ae-1111-4a2b-9c9d-000000000001</id>
      <publicationNumber>2026-08-26-0001</publicationNumber>
      <publicationState>PUBLISHED</publicationState>
      <publicationDate>{_PUB}</publicationDate>
      <expirationDate>{_EXP}</expirationDate>
      <cantons><canton>ZH</canton></cantons>
      <title><de>Badenerstrasse 120, 8004 Zürich — Dachausbau</de></title>
      <registrationOffice>
        <swissZipCode>8004</swissZipCode>
        <town>Zürich</town>
        <municipalityId>261</municipalityId>
        <displayName>Stadt Zürich</displayName>
      </registrationOffice>
    </publication>
    <publication>
      <id>c1f797ae-2222-4a2b-9c9d-000000000002</id>
      <publicationNumber>2026-08-26-0002</publicationNumber>
      <publicationState>PUBLISHED</publicationState>
      <publicationDate>{_PUB}</publicationDate>
      <expirationDate>{_EXP}</expirationDate>
      <cantons><canton>ZH</canton></cantons>
      <title><de>Seefeldstrasse 6, 8610 Uster — Neubau</de></title>
      <registrationOffice>
        <swissZipCode>8610</swissZipCode>
        <town>Uster</town>
        <municipalityId>198</municipalityId>
        <displayName>Stadt Uster</displayName>
      </registrationOffice>
    </publication>
  </publications>
</result>
"""

SAMPLE_XML_EMPTY = """<?xml version="1.0" encoding="UTF-8"?>
<result xmlns:ns2="http://amtsblattportal.ch/schemas/kabzh/1.26/BP-ZH01-export.xsd">
  <total>0</total>
  <publications/>
</result>
"""


def _fake_fetcher(xml_text: str) -> AmtsblattService:
    resp = MagicMock(spec=httpx.Response)
    resp.status_code = 200
    resp.text = xml_text
    resp.raise_for_status.return_value = None
    mock_client = AsyncMock(spec=httpx.AsyncClient)
    mock_client.get.return_value = resp
    return AmtsblattService(client=mock_client)


def _memory_pipeline(xml_text: str) -> AmtsblattNewsPipeline:
    return AmtsblattNewsPipeline(
        fetcher=_fake_fetcher(xml_text), repo=PlanningRepo(":memory:")
    )


async def test_spec_058_req_058_001_ac_058_001_ingest_real_xml_counts() -> None:
    pipe = _memory_pipeline(SAMPLE_XML_TWO)
    result = await pipe.ingest()
    assert result.ingested == 2
    assert result.skipped == 0


async def test_spec_058_req_058_006_ac_058_003_ingest_idempotent() -> None:
    pipe = _memory_pipeline(SAMPLE_XML_TWO)
    first = await pipe.ingest()
    second = await pipe.ingest()
    assert (first.ingested, first.skipped) == (2, 0)
    assert (second.ingested, second.skipped) == (0, 2)


async def test_spec_058_req_058_002_ac_058_001_ingest_trust_metadata() -> None:
    result = await _memory_pipeline(SAMPLE_XML_TWO).ingest()
    assert result.source != ""
    assert result.trust_state == "official_publication"
    assert result.fetched_at != ""


async def test_spec_058_req_058_004_ac_058_002_provider_failure_no_fake_data() -> None:
    mock_client = AsyncMock(spec=httpx.AsyncClient)
    mock_client.get.side_effect = httpx.ConnectError("offline")
    pipe = AmtsblattNewsPipeline(
        fetcher=AmtsblattService(client=mock_client), repo=PlanningRepo(":memory:")
    )
    result = await pipe.ingest()
    assert result.ingested == 0
    assert result.skipped == 0
    assert result.trust_state == "source_pending"
    assert result.trust_state != "official_measurement"


async def test_spec_058_req_058_005_ac_058_002_empty_feed_honest_pending() -> None:
    result = await _memory_pipeline(SAMPLE_XML_EMPTY).ingest()
    assert result.ingested == 0
    assert result.trust_state == "source_pending"


async def test_spec_047_req_047_002_ac_047_001_get_local_serves_stored() -> None:
    pipe = _memory_pipeline(SAMPLE_XML_TWO)
    await pipe.ingest()
    svc = LocalNewsService(repo=pipe.store)
    resp = svc.get_local("8004")
    assert resp.status == "success"
    assert len(resp.items) == 1
    item = resp.items[0]
    assert item.postcode == "8004"
    assert item.trust_state == "official_publication"
    assert item.source != ""
    assert item.source_url != ""
    assert resp.trust_state == "official_publication"
    assert resp.fetched_at != ""


async def test_spec_047_req_047_001_ac_047_001_get_local_postcode_filter() -> None:
    pipe = _memory_pipeline(SAMPLE_XML_TWO)
    await pipe.ingest()
    svc = LocalNewsService(repo=pipe.store)
    assert len(svc.get_local("8004").items) == 1
    assert len(svc.get_local("8610").items) == 1
    assert svc.get_local("8610").items[0].municipality == "Uster"


def test_spec_047_req_047_004_ac_047_002_get_local_empty_honest_pending() -> None:
    resp = LocalNewsService(repo=PlanningRepo(":memory:")).get_local("8004")
    assert resp.items == []
    assert resp.status == "source_pending"
    assert resp.trust_state == "source_pending"


def _seeded_service() -> LocalNewsService:
    repo: PlanningRepo = PlanningRepo(":memory:")
    svc = LocalNewsService(repo=repo)
    pipe = AmtsblattNewsPipeline(fetcher=_fake_fetcher(SAMPLE_XML_TWO), repo=repo)
    import asyncio

    asyncio.get_event_loop().run_until_complete(pipe.ingest())
    return svc


def test_spec_047_req_047_001_ac_047_001_api_contract() -> None:
    main_mod._local_news = _seeded_service()
    try:
        r = TestClient(app).get("/api/v1/news/local?postcode=8004")
        assert r.status_code == 200
        body = r.json()
        for key in ("postcode", "items", "status", "source", "trust_state", "fetched_at"):
            assert key in body, f"missing {key}"
        assert body["postcode"] == "8004"
        assert body["status"] == "success"
        assert len(body["items"]) == 1
        assert body["items"][0]["trust_state"] == "official_publication"
    finally:
        main_mod._local_news = LocalNewsService()


def test_spec_047_req_047_004_ac_047_002_api_empty_honest_pending() -> None:
    main_mod._local_news = LocalNewsService(repo=PlanningRepo(":memory:"))
    try:
        r = TestClient(app).get("/api/v1/news/local?postcode=9999")
        assert r.status_code == 200
        assert r.json()["status"] == "source_pending"
        assert r.json()["items"] == []
    finally:
        main_mod._local_news = LocalNewsService()


def test_spec_047_req_047_003_ac_047_003_api_invalid_postcode_422() -> None:
    assert TestClient(app).get("/api/v1/news/local?postcode=XYZ").status_code == 422


def test_spec_058_req_058_001_ac_058_001_api_ingest_contract() -> None:
    main_mod._amtsblatt_pipeline = _memory_pipeline(SAMPLE_XML_TWO)
    try:
        r = TestClient(app).post("/api/v1/connectors/amtsblatt/ingest")
        assert r.status_code == 200
        body = r.json()
        assert body["ingested"] == 2
        assert body["skipped"] == 0
        assert body["trust_state"] == "official_publication"
        r2 = TestClient(app).post("/api/v1/connectors/amtsblatt/ingest")
        assert r2.json()["skipped"] == 2
    finally:
        main_mod._amtsblatt_pipeline = AmtsblattNewsPipeline()
