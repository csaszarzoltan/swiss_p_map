from fastapi.testclient import TestClient

from src.main import app

c = TestClient(app)


def test_spec_055_req_055_001_ac_055_001_meteo_api():
    assert c.get("/api/v1/connectors/meteoswiss/current").status_code == 200


def test_spec_056_req_056_001_ac_056_001_vote_sync_api():
    assert c.post("/api/v1/connectors/voteinfo/sync").json()["count"] == 1


def test_spec_057_req_057_001_ac_057_001_transport_api():
    assert c.get("/api/v1/transport/departures?station=Zurich").json()["items"]


def test_spec_058_req_058_001_ac_058_001_amtsblatt_api():
    assert c.post("/api/v1/connectors/amtsblatt/ingest").json()["ingested"] == 1


def test_spec_059_req_059_004_ac_059_003_newsletter_requires_consent():
    assert (
        c.post(
            "/api/v1/newsletter/subscribe",
            json={"email": "a@example.ch", "postcode": "8004", "consent": False},
        ).status_code
        == 400
    )


def test_spec_060_req_060_001_ac_060_001_push_api():
    assert (
        c.post(
            "/api/v1/push/subscribe",
            json={"endpoint": "https://push.example/2", "p256dh": "x", "auth": "y"},
        ).json()["status"]
        == "subscribed"
    )
