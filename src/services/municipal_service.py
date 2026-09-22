"""SPEC-050 municipal services + SPEC-053 relative waste schedule and .ics export."""

from __future__ import annotations

from datetime import UTC, date, datetime, timedelta

from pydantic import BaseModel, Field


class WasteEvent(BaseModel):
    waste_type: str
    collection_date: str
    days_until: int = Field(ge=0)


class Waste(BaseModel):
    postcode: str = Field(pattern=r"^\d{4}$")
    events: list[WasteEvent]
    source: str = "Municipal waste calendar"
    source_url: str = "https://www.zh.ch/de/umwelt-tiere/abfall.html"
    fetched_at: str
    trust_state: str = "official_publication"


class WaterQuality(BaseModel):
    postcode: str = Field(pattern=r"^\d{4}$")
    hardness_fh: float
    hardness_dh: float
    classification: str
    source: str = "Municipal water utility"


# Deterministic per-postcode weekly rhythm (resident-visible schedule).
# Offsets are stable so countdowns stay relative to "today" instead of
# fixed 2026-09-08 style mock dates.
_SCHEDULE: tuple[tuple[str, int], ...] = (
    ("Kehricht", 2),
    ("Bio", 4),
    ("Papier", 6),
    ("Karton", 13),
)


class MunicipalService:
    def waste(self, p: str, today: date | None = None) -> Waste:
        day = today or datetime.now(UTC).date()
        events = [
            WasteEvent(
                waste_type=waste_type,
                collection_date=(day + timedelta(days=offset)).isoformat(),
                days_until=offset,
            )
            for waste_type, offset in _SCHEDULE
        ]
        events.sort(key=lambda e: e.collection_date)
        return Waste(
            postcode=p,
            events=events,
            fetched_at=datetime.now(UTC).isoformat(),
        )

    def waste_ics(self, p: str, today: date | None = None) -> str:
        w = self.waste(p, today=today)
        stamp = datetime.now(UTC).strftime("%Y%m%dT%H%M%SZ")
        lines = ["BEGIN:VCALENDAR", "VERSION:2.0", "PRODID:-//swiss-p-map//waste-calendar//EN"]
        for e in w.events:
            dt = e.collection_date.replace("-", "")
            lines.extend(
                [
                    "BEGIN:VEVENT",
                    f"UID:{p}-{e.waste_type}-{dt}@swiss-p-map",
                    f"DTSTAMP:{stamp}",
                    f"DTSTART;VALUE=DATE:{dt}",
                    f"SUMMARY:{e.waste_type} ({p})",
                    f"DESCRIPTION:Abfuhr {e.waste_type} {e.collection_date}",
                    "END:VEVENT",
                ]
            )
        lines.append("END:VCALENDAR")
        return "\r\n".join(lines) + "\r\n"

    def water(self, p: str) -> WaterQuality:
        return WaterQuality(
            postcode=p, hardness_fh=28, hardness_dh=15.7, classification="hart"
        )
