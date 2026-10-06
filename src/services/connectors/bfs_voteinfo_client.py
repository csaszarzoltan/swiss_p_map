"""BFS VoteInfo OGD fetch boundary (SPEC-056, SPEC-056b).

The live Swiss Federal VoteInfo OGD source is a constant host serving one JSON
document per vote Sunday:

    https://ogd-static.voteinfo-app.ch/v1/ogd/sd-t-17-02-{YYYYMMDD}-eidgAbstimmung.json

The fetch is always performed through an injected ``httpx.AsyncClient`` so unit
tests never need a socket (``httpx.MockTransport``); when no client is injected
a per-call client is created with the 10 s budget of SPEC-056 NFR-056-001.
"""

from __future__ import annotations

import hashlib
import json
import re
from typing import Any, Literal

import httpx
from pydantic import BaseModel

# SPEC-056b FR-01/FR-07: constant host, constant path, one 10 s budget per fetch.
OGD_HOST = "ogd-static.voteinfo-app.ch"
OGD_URL_TEMPLATE = (
    "https://ogd-static.voteinfo-app.ch/v1/ogd/sd-t-17-02-{vote_date}-eidgAbstimmung.json"
)
OGD_TIMEOUT_SECONDS = 10.0

# SPEC-056b R-3/R-6: the date is validated strictly; the host is never
# caller-controlled, so a malformed date cannot redirect the request.
VOTE_DATE_PATTERN = re.compile(r"^\d{8}$")


class VoteSync(BaseModel):
    count: int
    sha256: str
    source: str = "BFS VoteInfo"
    trust_state: Literal["official_publication", "stale", "source_pending"] = (
        "source_pending"
    )
    fetched_at: str | None = None
    poll_interval_seconds: int = 60


class VoteInfoFetchError(RuntimeError):
    """Raised when the VoteInfo OGD source cannot be read.

    A typed, catchable error: the caller decides how to label the response.
    This error never carries fabricated vote rows.
    """


class BfsVoteInfoClient:
    """Reads the live VoteInfo OGD publication for one vote Sunday."""

    def __init__(self, client: httpx.AsyncClient | None = None) -> None:
        self._client = client

    @staticmethod
    def build_url(vote_date: str) -> str:
        """Returns the OGD URL for ``vote_date`` (``YYYYMMDD``).

        Raises:
            ValueError: if ``vote_date`` is not exactly eight digits. The date
                is never guessed or defaulted here.
        """
        if not VOTE_DATE_PATTERN.match(vote_date):
            raise ValueError(
                f"vote_date must match ^\\d{{8}}$ (YYYYMMDD), got {vote_date!r}"
            )
        return OGD_URL_TEMPLATE.format(vote_date=vote_date)

    async def fetch(self, vote_date: str) -> tuple[dict[str, Any], str]:
        """Fetches and decodes the OGD document for ``vote_date``.

        Returns:
            The decoded payload and the exact URL it came from, so callers can
            name the real host in their response metadata.

        Raises:
            ValueError: malformed ``vote_date`` (caller error, never guessed).
            VoteInfoFetchError: transport error, non-200 status, or a body
                that is not a JSON object.
        """
        url = self.build_url(vote_date)
        if self._client is not None:
            return await self._get(self._client, url), url
        async with httpx.AsyncClient(timeout=OGD_TIMEOUT_SECONDS) as client:
            return await self._get(client, url), url

    @staticmethod
    async def _get(client: httpx.AsyncClient, url: str) -> dict[str, Any]:
        try:
            response = await client.get(url, timeout=OGD_TIMEOUT_SECONDS)
        except httpx.HTTPError as exc:
            raise VoteInfoFetchError(f"VoteInfo OGD unreachable ({url}): {exc}") from exc

        if response.status_code != 200:
            raise VoteInfoFetchError(
                f"VoteInfo OGD returned HTTP {response.status_code} ({url})"
            )

        try:
            data = response.json()
        except ValueError as exc:
            raise VoteInfoFetchError(f"VoteInfo OGD body is not JSON ({url})") from exc

        if not isinstance(data, dict):
            raise VoteInfoFetchError(f"VoteInfo OGD body is not an object ({url})")
        return data

    def sync(self) -> VoteSync:
        """Network-free probe for POST /api/v1/connectors/voteinfo/sync (SPEC-056c).

        Carries no vote rows and performs no I/O, so the response is a
        deterministic ``count=0`` with ``trust_state="source_pending"`` and
        ``fetched_at=None``. The live data path is
        ``VoteService.refresh_from_live()`` (SPEC-056b), not this method.
        """
        raw = json.dumps([], sort_keys=True).encode()
        return VoteSync(count=0, sha256=hashlib.sha256(raw).hexdigest())
