"""Live PARIS test — RED: politics_service should call PARIS, not stub."""

import httpx
import pytest

from src.services.politics_service import PoliticsService


@pytest.mark.asyncio
async def test_politics_paris_live_mock_8004() -> None:
    """Given mocked PARIS kontakt XML with Wahlkreis 4, 8004 → 2 reps."""
    xml = """<?xml version="1.0" encoding="UTF-8"?>
<cdws:SearchDetailResponse xmlns:cdws="http://www.cmiag.ch/cdws/1.0">
  <cdws:Result hits="2">
    <cdws:Kontakt><c>ID=111</c><c>Wahlkreis=4</c><c>NameVorname>Muster Anna</c><c>Partei>SP</c><c>AktivesRatsmitglied>true</c></cdws:Kontakt>
    <cdws:Kontakt><c>ID=112</c><c>Wahlkreis>4+5</c><c>NameVorname>Beispiel Hans</c><c>Partei>FDP</c></cdws:Kontakt>
  </cdws:Result>
</cdws:SearchDetailResponse>"""

    def handler(request: httpx.Request) -> httpx.Response:
        assert "kontakt" in str(request.url)
        return httpx.Response(
            200, content=xml.encode(), headers={"content-type": "application/xml"}
        )

    transport = httpx.MockTransport(handler)
    async with httpx.AsyncClient(transport=transport) as client:
        svc = PoliticsService(client=client)
        # keep sync get_by_postcode for E2E stub compatibility, add async live path
        data = await svc.get_by_postcode_live("8004")
        assert data is not None
        assert "4" in data.district_name or "4+5" in data.district_name
        assert len(data.representatives) >= 1
