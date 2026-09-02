"""BAKOM/OFCOM digital connectivity status (SPEC-042)."""
from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field


class ConnectivityStatus(BaseModel):
    postcode: str = Field(pattern=r"^\d{4}$")
    ftth_percent: float = Field(ge=0,le=100)
    mobile_5g_coverage: Literal["low","medium","high"]
    average_download_mbps: float = Field(ge=0)
    source: str = "BAKOM/OFCOM broadband and mobile coverage"
    quality_state: Literal["area_estimate"] = "area_estimate"
class ConnectivityService:
    def status(self, postcode: str) -> ConnectivityStatus:
        urban=postcode in {"8001","8004","3011","4001","1201"}
        return ConnectivityStatus(postcode=postcode,ftth_percent=92 if urban else 61,mobile_5g_coverage="high" if urban else "medium",average_download_mbps=850 if urban else 310)
