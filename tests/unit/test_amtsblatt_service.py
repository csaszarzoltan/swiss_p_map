"""Unit: Amtsblatt client — XML-only kontraktum, mockolt httpx. RED Task 2."""

from __future__ import annotations

from datetime import date
from unittest.mock import AsyncMock, MagicMock

import httpx
import pytest

from src.services.amtsblatt_service import AmtsblattService

SAMPLE_XML = """<?xml version=\"1.0\" encoding=\"UTF-8\"?>
<result xmlns:ns2=\"http://amtsblattportal.ch/schemas/kabzh/1.26/BP-ZH01-export.xsd\">
  <total>1</total>
  <publications>
    <publication>
      <id>c1f797ae-1111-4a2b-9c9d-000000000001</id>
      <publicationNumber>2026-08-26-0001</publicationNumber>
      <publicationState>PUBLISHED</publicationState>
      <publicationDate>2026-08-26</publicationDate>
      <expirationDate>2027-08-26</expirationDate>
      <cantons><canton>ZH</canton></cantons>
      <title><de>Seefeldstrasse 6, 8610 Uster — Neubau</de></title>
      <registrationOffice>
        <swissZipCode>8610</swissZipCode>
        <town>Uster</town>
        <municipalityId>198</municipalityId>
        <displayName>Stadt Uster</displayName>
      </registrationOffice>
      <legalRemedy>Auflage 20 Tage ab Publikation — Einsprache innert Auflagefrist.</legalRemedy>
    </publication>
  </publications>
</result>
"""

SAMPLE_XML_EMPTY = """<?xml version=\"1.0\" encoding=\"UTF-8\"?>
<result xmlns:ns2=\"http://amtsblattportal.ch/schemas/kabzh/1.26/BP-ZH01-export.xsd\">
  <total>0</total>
  <publications/>
</result>
"""


def _mock_xml_response(text: str) -> MagicMock:
    resp = MagicMock(spec=httpx.Response)
    resp.status_code = 200
    resp.text = text
    resp.raise_for_status.return_value = None
    return resp


@pytest.mark.asyncio
async def test_fetch_one_publication() -> None:
    mock_client = AsyncMock(spec=httpx.AsyncClient)
    mock_client.get.return_value = _mock_xml_response(SAMPLE_XML)
    svc = AmtsblattService(client=mock_client)
    items = await svc.fetch_publications(canton="ZH", since=date(2026, 8, 26))
    assert len(items) == 1
    b = items[0]
    assert b.municipality == "Uster"
    assert b.postcode == "8610"
    assert b.canton == "ZH"
    assert b.publication_date == date(2026, 8, 26)
    assert b.expiration_date == date(2027, 8, 26)
    assert b.auflage_end == date(2026, 9, 15)  # +20
    assert b.is_active(date(2026, 8, 27)) is True
    assert "amtsblattportal.ch" in b.source_url
    mock_client.get.assert_awaited_once()


@pytest.mark.asyncio
async def test_fetch_empty_returns_empty() -> None:
    mock_client = AsyncMock(spec=httpx.AsyncClient)
    mock_client.get.return_value = _mock_xml_response(SAMPLE_XML_EMPTY)
    svc = AmtsblattService(client=mock_client)
    items = await svc.fetch_publications(canton="ZH", since=date(2026, 8, 26))
    assert items == []


@pytest.mark.asyncio
async def test_fetch_http_error_returns_empty() -> None:
    mock_client = AsyncMock(spec=httpx.AsyncClient)
    mock_client.get.side_effect = httpx.ConnectError("offline")
    svc = AmtsblattService(client=mock_client)
    items = await svc.fetch_publications(canton="ZH", since=date(2026, 8, 26))
    assert items == []


@pytest.mark.asyncio
async def test_fetch_skips_malformed_entry() -> None:
    """One OK, one missing title — only the valid one is returned."""
    xml = SAMPLE_XML.replace(
        "<title><de>Seefeldstrasse 6",
        "<title><de>Good</de></title></publication><publication><id>bad",
    )
    # Simpler: two pubs, second without postcode -> skip
    xml2 = """<?xml version=\"1.0\" encoding=\"UTF-8\"?>
<result><total>2</total><publications>
  <publication><id>ok-1</id><title><de>Ok</de></title><registrationOffice><swissZipCode>8004</swissZipCode><town>Zürich</town></registrationOffice><publicationDate>2026-08-26</publicationDate><expirationDate>2027-08-26</expirationDate><cantons><canton>ZH</canton></cantons></publication>
  <publication><id>bad-1</id><title><de></de></title><registrationOffice><swissZipCode></swissZipCode><town></town></registrationOffice><publicationDate>2026-08-26</publicationDate><expirationDate>2027-08-26</expirationDate></publication>
</publications></result>"""
    mock_client = AsyncMock(spec=httpx.AsyncClient)
    mock_client.get.return_value = _mock_xml_response(xml2)
    svc = AmtsblattService(client=mock_client)
    items = await svc.fetch_publications(canton="ZH", since=date(2026, 8, 26))
    assert len(items) == 1
    assert items[0].id == "ok-1"
