"""HTTP acceptance tests mapping P1/P2 SPEC, REQ and AC identifiers."""

from fastapi.testclient import TestClient

from src.main import app

client = TestClient(app)


def test_spec_037_req_001_ac_001_microclimate_api() -> None:
    assert (
        client.get("/api/v1/climate/microclimate?postcode=8004&canton=ZH").json()[
            "source"
        ]
        == "MeteoSwiss / CH2025"
    )


def test_spec_038_req_001_ac_001_education_api() -> None:
    assert (
        len(
            client.get("/api/v1/education/facilities?postcode=8004").json()[
                "facilities"
            ]
        )
        == 3
    )


def test_spec_043_req_001_ac_001_energy_api() -> None:
    assert client.get("/api/v1/energy/assessment?postcode=8004").json()["checklist"]


def test_spec_040_req_001_ac_001_air_pollen_api() -> None:
    assert (
        "pm10_ug_m3"
        in client.get("/api/v1/environment/air-pollen?postcode=8004").json()[
            "pollutants"
        ]
    )


def test_spec_041_req_001_ac_001_healthcare_api() -> None:
    assert (
        len(client.get("/api/v1/healthcare/access?postcode=8004").json()["facilities"])
        == 3
    )


def test_spec_042_req_001_ac_001_connectivity_api() -> None:
    assert (
        client.get("/api/v1/connectivity/status?postcode=8004").json()[
            "mobile_5g_coverage"
        ]
        == "high"
    )
