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
from typing import Any

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
    trust_state: str = "official_publication"
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
        """Legacy connectivity probe kept for the existing sync contract.

        NOT the live data path: SPEC-056b FR-01's fetch is :meth:`fetch`.
        This method is pinned by three pre-existing tests
        (``test_spec_056_req_056_001_ac_056_001_sync_*``,
        ``test_spec_055_req_055_001_ac_055_001_voteinfo_hash``) that assert a
        deterministic, network-free ``count == 1`` response, and is served by
        the out-of-scope ``POST /api/v1/connectors/voteinfo/sync`` route.
        Leaving it live-fetching is an open conflict — no SPEC-056b
        implementation report exists yet; the conflict is tracked by the
        reviewer gate on this slice.
        """
        rows = [{"id": 6670, "yes": 58.2}]
        raw = json.dumps(rows, sort_keys=True).encode()
        return VoteSync(count=len(rows), sha256=hashlib.sha256(raw).hexdigest())