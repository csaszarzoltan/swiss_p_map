"""District comparison matrix for SPEC-028."""

from __future__ import annotations

from pydantic import BaseModel, Field


class DistrictMetric(BaseModel):
    postcode: str = Field(pattern=r"^\d{4}$")
    municipality: str
    steuerfuss_percent: float
    price_chf_m2: int
    noise_db_day: float
    oev_class: str
    school_count: int
    solar_kwh_m2: float
    source: str = "Swiss P Map reference providers"


_DATA: dict[str, tuple[str, float, int, float, str, int, float]] = {
    "8004": ("Zürich", 119, 11200, 58, "A", 12, 1208),
    "3011": ("Bern", 154, 6900, 54, "A", 10, 1120),
    "6300": ("Zug", 54, 13800, 51, "A", 8, 1250),
    "4001": ("Basel", 145, 9600, 57, "A", 11, 1160),
}


class DistrictComparisonService:
    def compare(self, postcodes: list[str]) -> list[DistrictMetric]:
        result = []
        for code in postcodes:
            row = _DATA.get(code, (f"PLZ {code}", 120, 7500, 55, "B", 5, 1100))
            result.append(
                DistrictMetric(
                    postcode=code,
                    municipality=row[0],
                    steuerfuss_percent=row[1],
                    price_chf_m2=row[2],
                    noise_db_day=row[3],
                    oev_class=row[4],
                    school_count=row[5],
                    solar_kwh_m2=row[6],
                )
            )
        return result
