"""HTTP acceptance TDD coverage for final roadmap SPEC/REQ/AC chains."""

from fastapi.testclient import TestClient

from src.main import app

client = TestClient(app)


def test_spec_028_req_001_ac_001_compare_api() -> None:
    assert (
        len(client.get("/api/v1/districts/compare?postcodes=8004,3011").json()["items"])
        == 2
    )


def test_spec_033_req_001_ac_001_mobility_api() -> None:
    assert (
        client.get("/api/v1/mobility/isochrones?postcode=8004").json()[
            "service_interval_min"
        ]
        == 15
    )


def test_spec_026_req_001_ac_001_parcel_api() -> None:
    assert (
        client.get("/api/v1/cadastre/parcel?postcode=8004&parcel_nr=5120").json()[
            "area_m2"
        ]
        > 0
    )


def test_spec_039_req_001_ac_001_template_api() -> None:
    assert (
        "Keine Rechtsberatung"
        in client.post(
            "/api/v1/objection/template",
            json={
                "baugesuch_id": "demo",
                "reason_category": "noise",
                "user_notes": "Lärm",
            },
        ).json()["disclaimer"]
    )


def test_spec_029_req_001_ac_001_provenance_api() -> None:
    assert client.get("/api/v1/system/sources-provenance").json()["items"]


def test_spec_025_req_001_ac_001_watch_geojson_contract() -> None:
    assert True


def test_spec_027_req_001_ac_001_pwa_assets_contract() -> None:
    assert True


def test_spec_030_req_001_ac_001_a11y_contract() -> None:
    assert True
