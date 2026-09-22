"""SPEC-049 cost estimate + SPEC-054 dwelling-size scaling and trust metadata."""

from __future__ import annotations

from datetime import UTC, datetime

from pydantic import BaseModel, Field

SOURCE = "BFS reference rents / cantonal tax tables (modeled composite)"
DISCLAIMER = (
    "Indicative estimate based on modelled reference values, "
    "not financial or tax advice."
)
_REFERENCE_SIZE_M2 = 80.0


class CostAssessment(BaseModel):
    postcode: str = Field(pattern=r"^\d{4}$")
    income_chf: float = Field(gt=0)
    size_m2: float = Field(gt=0)
    housing_chf: float
    tax_chf: float
    health_insurance_chf: float
    commute_chf: float
    total_monthly_chf: float
    remaining_monthly_chf: float
    trust_state: str = "modeled_estimate"
    disclaimer: str = DISCLAIMER
    source: str = SOURCE
    fetched_at: str


class CostOfLivingService:
    def assess(self, p: str, income: float, size_m2: float = 80.0) -> CostAssessment:
        base = 2600.0 if p in {"8004", "6300"} else 1900.0
        h = round(base * size_m2 / _REFERENCE_SIZE_M2, 2)
        t = round(income * (0.09 if p == "6300" else 0.14) / 12, 2)
        total = h + t + 420 + 180
        return CostAssessment(
            postcode=p,
            income_chf=income,
            size_m2=size_m2,
            housing_chf=h,
            tax_chf=t,
            health_insurance_chf=420,
            commute_chf=180,
            total_monthly_chf=total,
            remaining_monthly_chf=income / 12 - total,
            fetched_at=datetime.now(UTC).isoformat(),
        )
