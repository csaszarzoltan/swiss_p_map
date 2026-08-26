from fastapi.testclient import TestClient

from src.main import app

client = TestClient(app)

def test_health() -> None:
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json()["status"] == "ok"
    assert r.json()["app"] == "swiss-p-map"

def test_geo_convert_ok() -> None:
    r = client.get("/api/v1/geo/convert", params={"easting": 2683100, "northing": 1248100})
    assert r.status_code == 200
    assert abs(r.json()["wgs84"]["latitude"] - 47.378) < 0.01

def test_geo_convert_bad_bounds() -> None:
    r = client.get("/api/v1/geo/convert", params={"easting": 1000000, "northing": 1200000})
    assert r.status_code == 400

def test_politics_known_postcode() -> None:
    r = client.get("/api/v1/politics/representatives", params={"postcode": "8004"})
    assert r.status_code == 200
    assert "Wahlkreis" in r.json()["district_name"]
    assert len(r.json()["representatives"]) > 0

def test_politics_unknown_postcode() -> None:
    r = client.get("/api/v1/politics/representatives", params={"postcode": "9999"})
    assert r.status_code == 404

def test_place_known_postcode() -> None:
    r = client.get("/api/v1/place/8004")
    assert r.status_code == 200
    assert r.json()["canton"] == "ZH"

def test_place_unknown() -> None:
    r = client.get("/api/v1/place/9999")
    assert r.status_code == 404


def test_cors_preflight() -> None:
    r = client.options(
        "/api/v1/place/8004",
        headers={"Origin": "http://localhost:3000", "Access-Control-Request-Method": "GET"},
    )
    assert r.status_code in (200, 204)
    assert r.headers.get("access-control-allow-origin") == "http://localhost:3000"


def test_planning_baugesuche_empty_ok() -> None:
    r = client.get("/api/v1/planning/baugesuche")
    assert r.status_code == 200
    assert "items" in r.json()
    assert isinstance(r.json()["items"], list)


def test_planning_baugesuche_postcode_filter() -> None:
    r = client.get("/api/v1/planning/baugesuche", params={"postcode": "8004"})
    assert r.status_code == 200
    for item in r.json()["items"]:
        assert item["postcode"] == "8004"


def test_planning_baugesuche_active_only_param() -> None:
    r = client.get("/api/v1/planning/baugesuche", params={"active_only": "false"})
    assert r.status_code == 200
    assert "items" in r.json()
