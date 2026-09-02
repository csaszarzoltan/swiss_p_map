from fastapi.testclient import TestClient

from src.main import app

c = TestClient(app)


def test_spec_045_req_045_001_ac_045_001_briefing_api():
    assert c.get("/api/v1/local/briefing?postcode=8004").status_code == 200


def test_spec_046_req_046_001_ac_046_001_vote_api():
    assert (
        c.get("/api/v1/votes/proposals/6801/analysis").json()["polls"][0][
            "margin_percent"
        ]
        == 2.8
    )


def test_spec_046_req_046_003_ac_046_003_vote_404():
    assert c.get("/api/v1/votes/proposals/1/analysis").status_code == 404


def test_spec_047_req_047_004_ac_047_002_news_api():
    assert (
        c.get("/api/v1/news/local?postcode=8004").json()["status"] == "source_pending"
    )


def test_spec_048_req_048_001_ac_048_001_weather_api():
    assert c.get("/api/v1/weather/alerts").json()["items"]


def test_spec_049_req_049_003_ac_049_003_negative_income():
    assert (
        c.get("/api/v1/costs/assessment?postcode=8004&income_chf=-1").status_code == 422
    )


def test_spec_050_req_050_001_ac_050_001_municipal_api():
    assert (
        c.get("/api/v1/municipal/water-quality?postcode=8004").json()["hardness_fh"]
        == 28
    )
