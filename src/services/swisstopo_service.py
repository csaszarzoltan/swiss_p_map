"""Swisstopo search service — DI-friendly, httpx-injected.

Wraps ``api3.geo.admin.ch`` / ``map.geo.admin.ch`` search.
In tests the httpx client is mocked; no real HTTP required.
"""

from __future__ import annotations

from typing import Protocol

import httpx

from src.models.geo import AddressSearchResult, CoordinateLV95, CoordinateWGS84
from src.services.geo_converter import lv95_to_wgs84

SEARCH_URL = "https://api3.geo.admin.ch/rest/services/api/SearchServer"


class SearchClient(Protocol):
    async def get(self, url: str, params: dict[str, object]) -> httpx.Response: ...


class SwisstopoService:
    """Geocoding via Swisstopo SearchServer.

    Args:
        client: httpx AsyncClient (injected — allows mocking).
        search_url: override for tests.
    """

    def __init__(
        self,
        client: httpx.AsyncClient | None = None,
        search_url: str = SEARCH_URL,
    ) -> None:
        self._client = client
        self._search_url = search_url

    async def search(self, query: str, limit: int = 5) -> list[AddressSearchResult]:
        """Search addresses / places.

        Returns empty list on no results or on HTTP error (never raises for transient failures
        — caller can distinguish via empty result).
        """
        params: dict[str, str | int] = {
            "searchText": query,
            "type": "locations",
            "limit": limit,
        }
        try:
            if self._client is not None:
                resp = await self._client.get(self._search_url, params=params)
            else:
                async with httpx.AsyncClient(timeout=10) as c:
                    resp = await c.get(self._search_url, params=params)
            resp.raise_for_status()
            data = resp.json()
        except (httpx.HTTPError, ValueError):
            return []

        results: list[AddressSearchResult] = []
        for feat in data.get("results", []):
            attrs = feat.get("attrs", {})
            try:
                x = float(attrs["x"])
                y = float(attrs["y"])
                label: str = str(attrs.get("label", query))
                canton: str = str(attrs.get("detail", ""))[:2] or "ZH"
                # attrs.x = LV95 easting, attrs.y = LV95 northing (swisstopo convention)
                lat, lon = lv95_to_wgs84(x, y)
                results.append(
                    AddressSearchResult(
                        label=label,
                        wgs84=CoordinateWGS84(latitude=lat, longitude=lon),
                        lv95=CoordinateLV95(easting=x, northing=y),
                        canton=canton,
                        municipality=label.split(",")[-1].strip() if "," in label else label,
                        postcode=None,
                    )
                )
            except (ValueError, KeyError, TypeError):
                continue
        return results
