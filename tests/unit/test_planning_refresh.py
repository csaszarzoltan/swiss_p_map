"""Planning refresh — RED: POST /api/v1/planning/refresh live Amtsblatt."""

from unittest.mock import AsyncMock, MagicMock

import httpx
import pytest
from fastapi.testclient import TestClient

from src.main import app
from src.services.amtsblatt_service import AmtsblattService

client = TestClient(app)


def _mock_xml_response(text: str) -> MagicMock:
    resp = MagicMock(spec=httpx.Response)
    resp.status_code = 200
    resp.text = text
    resp.raise_for_status.return_value = None
    return resp


# envelope must match amtsblatt_service: <result><publications><publication>
SAMPLE_REFRESH_XML = """<?xml version="1.0" encoding="UTF-8"?>
<result xmlns:ns2="http://amtsblattportal.ch/schemas/kabzh/1.26/BP-ZH01-export.xsd">
  <total>1</total>
  <publications>
    <publication>
      <id>test-refresh-1</id>
      <title><de>Teststrasse 1, 8004 Zürich — Neubau Test</de></title>
      <registrationOffice><swissZipCode>8004</swissZipCode><town>Zürich</town><municipalityId>261</municipalityId></registrationOffice>
      <publicationDate>2026-08-27</publicationDate>
      <expirationDate>2027-08-27</expirationDate>
      <cantons><canton>ZH</canton></cantons>
    </publication>
  </publications>
</result>"""


def test_planning_refresh_endpoint_exists() -> None:
    r = client.post("/api/v1/planning/refresh", json={})
    # Should be 200 with count or 502 if upstream down, but not 404/405
    assert r.status_code in (200, 502)
    if r.status_code == 200:
        assert "count" in r.json() or "items" in r.json() or "refreshed" in r.json()


@pytest.mark.asyncio
async def test_planning_service_refresh_mock() -> None:
    """Mock Amtsblatt XML → refresh upserts and returns count (active_only=False to avoid today<publication_date guard)."""
    mock_client = AsyncMock(spec=httpx.AsyncClient)
    mock_client.get.return_value = _mock_xml_response(SAMPLE_REFRESH_XML)
    from src.db.planning_repo import PlanningRepo
    from src.services.planning_service import PlanningService

    svc = PlanningService(fetcher=AmtsblattService(client=mock_client), repo=PlanningRepo(db_path=":memory:"))
    count = await svc.refresh(canton="ZH")
    assert count >= 1
    # publication_date is tomorrow (2026-08-27 vs today 2026-08-26) — active_only=True would filter it out
    items = svc.list_items(postcode="8004", active_only=False)
    assert any(i.id == "test-refresh-1" for i in items)
