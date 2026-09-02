"""Swiss canton tax comparison service (SPEC-032)."""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field

SOURCE = "Kantonale Steuerverwaltungen / ESTV comparison reference"

# Comparable municipal/cantonal index used by the product, all 26 cantons.
_RATES: dict[str, float] = {
    "ZH": 119.0,
    "BE": 154.0,
    "LU": 116.0,
    "UR": 100.0,
    "SZ": 60.0,
    "OW": 85.0,
    "NW": 65.0,
    "GL": 118.0,
    "ZG": 54.0,
    "FR": 138.0,
    "SO": 125.0,
    "BS": 145.0,
    "BL": 132.0,
    "SH": 112.0,
    "AR": 104.0,
    "AI": 96.0,
    "SG": 124.0,
    "GR": 108.0,
    "AG": 112.0,
    "TG": 117.0,
    "TI": 120.0,
    "VD": 150.0,
    "VS": 130.0,
    "NE": 156.0,
    "GE": 155.0,
    "JU": 157.0,
}
_NEIGHBORS: dict[str, list[str]] = {
    "ZH": ["AG", "SH", "TG", "SZ", "ZG"],
    "BE": ["FR", "JU", "LU", "NE", "SO", "VD", "VS"],
    "ZG": ["ZH", "SZ", "LU"],
    "SZ": ["ZG", "ZH", "LU", "UR", "GL"],
}


class TaxEntry(BaseModel):
    canton: str
    steuerfuss_percent: float = Field(ge=0)
    national_rank: int = Field(ge=1, le=26)
    band: Literal["low", "medium", "high"]


class TaxComparison(BaseModel):
    canton: str
    national_average_percent: float
    selected: TaxEntry
    ranking: list[TaxEntry]
    neighboring_cantons: list[TaxEntry]
    source: str = SOURCE
    quality_state: Literal["reference"] = "reference"


def _band(value: float) -> Literal["low", "medium", "high"]:
    if value < 90:
        return "low"
    if value < 135:
        return "medium"
    return "high"


class TaxService:
    """Compare a canton against all cantons and its geographic neighbors."""

    def compare(self, canton: str) -> TaxComparison | None:
        code = canton.upper()
        if code not in _RATES:
            return None
        ordered = sorted(_RATES.items(), key=lambda item: (item[1], item[0]))
        ranking = [
            TaxEntry(canton=c, steuerfuss_percent=v, national_rank=i, band=_band(v))
            for i, (c, v) in enumerate(ordered, 1)
        ]
        by_code = {item.canton: item for item in ranking}
        neighbors = [by_code[c] for c in _NEIGHBORS.get(code, [])]
        return TaxComparison(
            canton=code,
            national_average_percent=round(sum(_RATES.values()) / 26, 2),
            selected=by_code[code],
            ranking=ranking,
            neighboring_cantons=neighbors,
        )
