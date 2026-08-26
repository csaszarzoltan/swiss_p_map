"""Place service — Zürich pilot stub."""

from __future__ import annotations

from src.models.place import OeVGueteklasse, PlaceInfo

_STUBS: dict[str, PlaceInfo] = {
    "8004": PlaceInfo(
        postcode="8004",
        municipality="Zürich",
        canton="ZH",
        steuerfuss_percent=119.0,
        noise_db_day=62.5,
        oev_class=OeVGueteklasse.A,
        gwr_building_count=3420,
    ),
    "8001": PlaceInfo(
        postcode="8001",
        municipality="Zürich",
        canton="ZH",
        steuerfuss_percent=119.0,
        noise_db_day=58.0,
        oev_class=OeVGueteklasse.A,
        gwr_building_count=1890,
    ),
}


class PlaceService:
    def get_by_postcode(self, postcode: str) -> PlaceInfo | None:
        return _STUBS.get(postcode.strip())

    def list_postcodes(self) -> list[str]:
        return sorted(_STUBS.keys())
