"""SPEC-054 contract: full cost breakdown + size param + trust metadata.

TDD RED first: CostOfLivingService must expose housing/tax/health/commute/
remaining rows that sum to the total, scale housing with dwelling size,
and carry modeled_estimate trust metadata (never official_measurement).
"""

from __future__ import annotations

from fastapi.testclient import TestClient

from src.main import app
from src.services.cost_of_living_service import CostOfLivingService

c = TestClient(app)


def test_spec_054_req_054_001_ac_054_001_breakdown_rows_sum_to_total() -> None:
    x = CostOfLivingService().assess("8004", 120000, 80)
    assert x.housing_chf > 0
    assert x.tax_chf > 0
    assert x.health_insurance_chf > 0
    assert x.commute_chf > 0
    parts = x.housing_chf + x.tax_chf + x.health_insurance_chf + x.commute_chf
    assert x.total_monthly_chf == parts
    assert x.remaining_monthly_chf == 120000 / 12 - x.total_monthly_chf


def test_spec_054_req_054_001_ac_054_001_size_scales_housing() -> None:
    svc = CostOfLivingService()
    small = svc.assess("8004", 120000, 40)
    ref = svc.assess("8004", 120000, 80)
    big = svc.assess("8004", 120000, 160)
    assert small.housing_chf < ref.housing_chf < big.housing_chf
    assert small.size_m2 == 40
    assert big.size_m2 == 160


def test_spec_054_req_054_002_ac_054_001_trust_source_metadata() -> None:
    x = CostOfLivingService().assess("8004", 120000, 80)
    assert x.trust_state == "modeled_estimate"
    assert x.trust_state != "official_measurement"
    assert x.disclaimer != ""
    assert x.source != ""
    assert x.fetched_at != ""


def test_spec_054_req_054_001_ac_054_001_api_contract_with_size() -> None:
    r = c.get("/api/v1/costs/assessment?postcode=8004&income_chf=120000&size_m2=100")
    assert r.status_code == 200
    body = r.json()
    for key in (
        "housing_chf",
        "tax_chf",
        "health_insurance_chf",
        "commute_chf",
        "total_monthly_chf",
        "remaining_monthly_chf",
        "trust_state",
        "disclaimer",
        "source",
        "fetched_at",
    ):
        assert key in body, f"missing {key}"
    assert body["trust_state"] == "modeled_estimate"
    assert body["size_m2"] == 100


def test_spec_054_req_054_001_ac_054_001_api_contract_default_size() -> None:
    r = c.get("/api/v1/costs/assessment?postcode=8004&income_chf=120000")
    assert r.status_code == 200
    assert r.json()["total_monthly_chf"] > 0


def test_spec_054_req_054_003_ac_054_003_invalid_input_422() -> None:
    assert c.get("/api/v1/costs/assessment?postcode=XYZ&income_chf=120000").status_code == 422
    assert c.get("/api/v1/costs/assessment?postcode=8004&income_chf=0").status_code == 422
    assert c.get("/api/v1/costs/assessment?postcode=8004&income_chf=120000&size_m2=0").status_code == 422
