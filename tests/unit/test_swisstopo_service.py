from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock

import httpx
import pytest

from src.services.swisstopo_service import SwisstopoService

ZH_HB_ATTRS = {
    "x": 2683100.0,
    "y": 1248100.0,
    "label": "Zürich HB, 8001 Zürich",
    "detail": "ZH detail",
}


def _mock_response(results: list[dict[str, object]]) -> MagicMock:
    resp = MagicMock(spec=httpx.Response)
    resp.json.return_value = {"results": results}
    resp.raise_for_status.return_value = None
    return resp


@pytest.mark.asyncio
async def test_swisstopo_search_returns_results() -> None:
    mock_client = AsyncMock(spec=httpx.AsyncClient)
    mock_client.get.return_value = _mock_response([{"attrs": ZH_HB_ATTRS}])

    svc = SwisstopoService(client=mock_client)
    results = await svc.search("Zürich HB")

    assert len(results) == 1
    assert results[0].canton == "ZH"
    assert abs(results[0].wgs84.latitude - 47.378) < 0.01
    mock_client.get.assert_awaited_once()


@pytest.mark.asyncio
async def test_swisstopo_search_empty_on_no_results() -> None:
    mock_client = AsyncMock(spec=httpx.AsyncClient)
    mock_client.get.return_value = _mock_response([])

    svc = SwisstopoService(client=mock_client)
    results = await svc.search("unknown xyz 9999")

    assert results == []


@pytest.mark.asyncio
async def test_swisstopo_search_empty_on_http_error() -> None:
    mock_client = AsyncMock(spec=httpx.AsyncClient)
    mock_client.get.side_effect = httpx.ConnectError("offline")

    svc = SwisstopoService(client=mock_client)
    results = await svc.search("Zürich")

    assert results == []


@pytest.mark.asyncio
async def test_swisstopo_search_skips_invalid_coords() -> None:
    """Features with out-of-bounds coords are skipped, valid ones kept."""
    mock_client = AsyncMock(spec=httpx.AsyncClient)
    mock_client.get.return_value = _mock_response(
        [
            {
                "attrs": {"x": 1_000_000.0, "y": 1_200_000.0, "label": "bad"}
            },  # outside LV95
            {"attrs": ZH_HB_ATTRS},
        ]
    )

    svc = SwisstopoService(client=mock_client)
    results = await svc.search("test")

    assert len(results) == 1
    assert results[0].label == "Zürich HB, 8001 Zürich"
