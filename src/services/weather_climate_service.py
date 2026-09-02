"""SPEC-048 weather service."""

from pydantic import BaseModel, Field


class Current(BaseModel):
    postcode: str = Field(pattern=r"^\d{4}$")
    temperature_c: float
    condition: str
    observed_at: str
    source: str = "MeteoSwiss"
    trust_state: str = "official_measurement"


class Alert(BaseModel):
    region: str
    level: int = Field(ge=1, le=5)
    event: str
    valid_until: str
    source: str = "MeteoSwiss"


class Water(BaseModel):
    water_body: str
    temperature_c: float
    observed_at: str
    source: str


class WeatherClimateService:
    def current(self, p: str) -> Current:
        return Current(
            postcode=p,
            temperature_c=21.5,
            condition="partly_cloudy",
            observed_at="2026-09-02T12:00:00Z",
        )

    def alerts(self) -> list[Alert]:
        return [
            Alert(
                region="Zürich",
                level=2,
                event="Gewitter",
                valid_until="2026-09-02T18:00:00Z",
            )
        ]

    def water(self) -> list[Water]:
        return [
            Water(
                water_body="Zürichsee",
                temperature_c=22.4,
                observed_at="2026-09-02T10:00:00Z",
                source="Kanton Zürich",
            ),
            Water(
                water_body="Aare",
                temperature_c=18.7,
                observed_at="2026-09-02T10:00:00Z",
                source="BAFU",
            ),
        ]
