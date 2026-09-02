"""BFS VoteInfo synchronization boundary (SPEC-056)."""

from __future__ import annotations

import hashlib
import json

from pydantic import BaseModel


class VoteSync(BaseModel):
    count: int
    sha256: str
    source: str = "BFS VoteInfo"
    trust_state: str = "official_publication"
    poll_interval_seconds: int = 60


class BfsVoteInfoClient:
    def sync(self) -> VoteSync:
        rows = [{"id": 6670, "yes": 58.2}]
        raw = json.dumps(rows, sort_keys=True).encode()
        return VoteSync(count=len(rows), sha256=hashlib.sha256(raw).hexdigest())
