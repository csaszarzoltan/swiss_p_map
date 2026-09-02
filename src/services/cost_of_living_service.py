"""SPEC-049 cost estimate."""

from pydantic import BaseModel, Field


class CostAssessment(BaseModel):
    postcode: str = Field(pattern=r"^\d{4}$")
    income_chf: float = Field(gt=0)
    housing_chf: float
    tax_chf: float
    health_insurance_chf: float
    commute_chf: float
    total_monthly_chf: float
    remaining_monthly_chf: float
    trust_state: str = "modeled_estimate"
    disclaimer: str = "Indicative estimate, not financial or tax advice."


class CostOfLivingService:
    def assess(self, p: str, income: float) -> CostAssessment:
        h = 2600.0 if p in {"8004", "6300"} else 1900.0
        t = round(income * (0.09 if p == "6300" else 0.14) / 12, 2)
        total = h + t + 420 + 180
        return CostAssessment(
            postcode=p,
            income_chf=income,
            housing_chf=h,
            tax_chf=t,
            health_insurance_chf=420,
            commute_chf=180,
            total_monthly_chf=total,
            remaining_monthly_chf=income / 12 - total,
        )
