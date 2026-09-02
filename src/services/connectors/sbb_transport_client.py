"""SBB/OpenTransportData departure adapter (SPEC-057)."""

from pydantic import BaseModel


class Departure(BaseModel):
    station: str
    destination: str
    minutes: int
    category: str
    last_night_service: bool = False


class SbbTransportClient:
    def departures(self, station: str) -> list[Departure]:
        return [
            Departure(station=station, destination="Bern", minutes=4, category="IC"),
            Departure(
                station=station,
                destination="Zug",
                minutes=11,
                category="IR",
                last_night_service=True,
            ),
        ]
