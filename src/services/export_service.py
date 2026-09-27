"""Export audit-csomag — SPEC-020 (place+solar+oereb+steuerfuss+planning + provenance, JSON+CSV).

CSV: `;` elvalaszto (svajci konvencio), header row, UTF-8 with BOM optional but not required.
Provenance per source via `fetched_at` + `trust_state` (source_pending when missing).
"""

from __future__ import annotations

import csv
import io
import json
from datetime import UTC, datetime
from typing import Any

from src.models.place import PlaceInfo
from src.services.place_service import PlaceService
from src.services.planning_service import PlanningService

_TRUST_BY_SOURCE: dict[str, str] = {
    "place": "official_measurement",
    "solar": "official_measurement",
    "oereb": "cadastral_registry",
    "steuerfuss": "official_publication",
    "planning": "official_publication",
}

_SOURCE_LABEL: dict[str, str] = {
    "place": "api3.geo.admin.ch / PlaceService (ARE_OeV, BAFU_Laerm, BFE_Solar, ZH_WFS)",
    "solar": "BFE Sonnendach",
    "oereb": "OEREB Kataster (ZH WFS / geodienste.ch OGC API)",
    "steuerfuss": "Kantonale Steuerverwaltung / ESTV",
    "planning": "Amtsblattportal (Baugesuche)",
}


def _iso_now() -> str:
    return datetime.now(UTC).replace(microsecond=0).isoformat()


class ExportService:
    """Build audit export payload for a PLZ.

    Aggregates PlaceInfo + planning; other domains (solar, oereb, steuerfuss) are
    already embedded in PlaceInfo or derived from it. Trust/provenance is honest:
    missing values get source_pending rather than invented data.
    """

    def __init__(
        self,
        place: PlaceService | None = None,
        planning: PlanningService | None = None,
    ) -> None:
        self._place = place or PlaceService()
        self._planning = planning or PlanningService()

    def _sources(self, place: PlaceInfo | None, planning_items: list[dict[str, Any]]) -> list[dict[str, str]]:
        now = _iso_now()
        sources: list[dict[str, str]] = []
        # place aggregate
        sources.append({
            "id": "place",
            "source": _SOURCE_LABEL["place"],
            "fetched_at": now,
            "trust_state": "official_measurement" if place is not None else "source_pending",
        })
        # solar (inside place)
        has_solar = place is not None and place.solar_kwh_m2 is not None
        sources.append({
            "id": "solar",
            "source": _SOURCE_LABEL["solar"],
            "fetched_at": now,
            "trust_state": "official_measurement" if has_solar else "source_pending",
        })
        # oereb
        has_oereb = place is not None and place.oereb_zone is not None
        sources.append({
            "id": "oereb",
            "source": _SOURCE_LABEL["oereb"],
            "fetched_at": now,
            "trust_state": "cadastral_registry" if has_oereb else "source_pending",
        })
        # steuerfuss
        has_steuer = place is not None and place.steuerfuss_percent is not None
        sources.append({
            "id": "steuerfuss",
            "source": _SOURCE_LABEL["steuerfuss"],
            "fetched_at": now,
            "trust_state": "official_publication" if has_steuer else "source_pending",
        })
        # planning
        sources.append({
            "id": "planning",
            "source": _SOURCE_LABEL["planning"],
            "fetched_at": now,
            "trust_state": "official_publication" if planning_items else "source_pending",
        })
        return sources

    def build(self, postcode: str) -> dict[str, Any] | None:
        code = postcode.strip()
        if not code.isdigit() or len(code) != 4:
            return None
        place = self._place.get_by_postcode(code)
        if place is None:
            return None
        planning_items = self._planning.list_items(postcode=code, active_only=False)
        now = _iso_now()
        return {
            "postcode": code,
            "fetched_at": now,
            "sources": self._sources(place, [p.model_dump(mode="json") for p in planning_items]),
            "data": {
                "place": place.model_dump(),
                "solar": {
                    "kwh_m2": place.solar_kwh_m2,
                    "class": place.solar_class,
                    "source": _SOURCE_LABEL["solar"],
                    "trust_state": "official_measurement" if place.solar_kwh_m2 is not None else "source_pending",
                },
                "oereb": {
                    "zone": place.oereb_zone,
                    "source": _SOURCE_LABEL["oereb"],
                    "trust_state": "cadastral_registry" if place.oereb_zone is not None else "source_pending",
                },
                "steuerfuss": {
                    "percent": place.steuerfuss_percent,
                    "source": place.steuerfuss_source,
                    "trust_state": "official_publication" if place.steuerfuss_percent is not None else "source_pending",
                },
                "planning": {
                    "count": len(planning_items),
                    "items": [p.model_dump(mode="json") for p in planning_items],
                    "source": _SOURCE_LABEL["planning"],
                    "trust_state": "official_publication" if planning_items else "source_pending",
                },
                "municipality": place.municipality,
                "canton": place.canton,
            },
        }

    def to_json(self, postcode: str) -> str | None:
        payload = self.build(postcode)
        if payload is None:
            return None
        return json.dumps(payload, ensure_ascii=False, indent=2)

    def to_csv(self, postcode: str) -> str | None:
        payload = self.build(postcode)
        if payload is None:
            return None
        place: dict[str, Any] = payload["data"]["place"]
        planning_items: list[dict[str, Any]] = payload["data"]["planning"]["items"]
        buf = io.StringIO()
        w = csv.writer(buf, delimiter=";", lineterminator="\n", quoting=csv.QUOTE_MINIMAL)
        # Provenance header as comment-like row? Instead header rows + provenance section
        w.writerow(["section", "field", "value", "source", "trust_state", "fetched_at"])
        fetched = payload["fetched_at"]
        # place row group
        for field in ("postcode", "municipality", "canton", "steuerfuss_percent", "noise_db_day", "oev_class", "gwr_building_count", "solar_kwh_m2", "solar_class", "oereb_zone", "steuerfuss_source"):
            val = place.get(field)
            # derive trust per field
            trust = "official_measurement" if val not in (None, "", "none") else "source_pending"
            if field in ("solar_kwh_m2", "solar_class"):
                trust = "official_measurement" if place.get("solar_kwh_m2") is not None else "source_pending"
            if field == "oereb_zone":
                trust = "cadastral_registry" if val not in (None, "") else "source_pending"
            w.writerow(["place", field, "" if val is None else str(val), _SOURCE_LABEL.get(field, _SOURCE_LABEL["place"]), trust, fetched])
        # solar convenience
        solar = payload["data"]["solar"]
        w.writerow(["solar", "kwh_m2", "" if solar["kwh_m2"] is None else str(solar["kwh_m2"]), solar["source"], solar["trust_state"], fetched])
        w.writerow(["solar", "class", solar["class"] or "", solar["source"], solar["trust_state"], fetched])
        # oereb
        oereb = payload["data"]["oereb"]
        w.writerow(["oereb", "zone", oereb["zone"] or "", oereb["source"], oereb["trust_state"], fetched])
        # steuerfuss
        steuer = payload["data"]["steuerfuss"]
        w.writerow(["steuerfuss", "percent", "" if steuer["percent"] is None else str(steuer["percent"]), steuer["source"], steuer["trust_state"], fetched])
        # planning header + items (flatten 1 row per baugesuch with key fields)
        w.writerow(["planning", "count", str(payload["data"]["planning"]["count"]), payload["data"]["planning"]["source"], payload["data"]["planning"]["trust_state"], fetched])
        for item in planning_items:
            w.writerow([
                "planning_item",
                item.get("id", ""),
                item.get("title", "")[:120],
                item.get("source_url", ""),
                "official_publication",
                item.get("publication_date", ""),
            ])
        # sources provenance footer rows
        for s in payload["sources"]:
            w.writerow(["source", s["id"], s["source"], s["source"], s["trust_state"], s["fetched_at"]])
        return buf.getvalue()
