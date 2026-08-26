import pytest
from httpx import AsyncClient, ASGITransport

# We attempt to import the FastAPI app from src.main once implemented
# For black-box E2E test execution:
try:
    from src.main import app
except ImportError:
    app = None

BASE_URL = "http://testserver"

@pytest.mark.asyncio
async def test_health_check_e2e():
    """E2E API test: Verify health check endpoint returns 200 and valid status."""
    if app is None:
        pytest.fail("src.main.app is not yet implemented by developer agent.")
    
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url=BASE_URL) as client:
        response = await client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"
        assert data["app"] == "swiss-p-map"
        assert "version" in data

@pytest.mark.asyncio
async def test_geo_convert_lv95_to_wgs84_e2e():
    """E2E API test: Verify coordinate conversion endpoint from LV95 to WGS84."""
    if app is None:
        pytest.fail("src.main.app is not yet implemented by developer agent.")
    
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url=BASE_URL) as client:
        response = await client.get(
            "/api/v1/geo/convert",
            params={"easting": 2683100.0, "northing": 1248100.0}
        )
        assert response.status_code == 200
        data = response.json()
        assert "wgs84" in data
        assert abs(data["wgs84"]["latitude"] - 47.3781) < 0.01
        assert abs(data["wgs84"]["longitude"] - 8.5401) < 0.01

@pytest.mark.asyncio
async def test_politics_representatives_by_postcode_e2e():
    """E2E API test: Verify representative lookup by Swiss postcode."""
    if app is None:
        pytest.fail("src.main.app is not yet implemented by developer agent.")
    
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url=BASE_URL) as client:
        response = await client.get(
            "/api/v1/politics/representatives",
            params={"postcode": "8004"}
        )
        assert response.status_code == 200
        data = response.json()
        assert "district_name" in data
        assert "Wahlkreis" in data["district_name"]
        assert "representatives" in data
        assert len(data["representatives"]) > 0
        first_rep = data["representatives"][0]
        assert "name" in first_rep
        assert "party" in first_rep
        assert "proposals" in first_rep
