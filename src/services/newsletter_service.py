"""Privacy-minimal double-opt-in newsletter state machine (SPEC-059)."""

from __future__ import annotations

import hashlib
import secrets

from pydantic import BaseModel, Field


class SubscribeRequest(BaseModel):
    email: str = Field(pattern=r"^[^@ ]+@[^@ ]+\.[^@ ]+$")
    postcode: str = Field(pattern=r"^\d{4}$")
    consent: bool


class NewsletterService:
    def __init__(self) -> None:
        self._pending: dict[str, str] = {}
        self._active: set[str] = set()

    def subscribe(self, r: SubscribeRequest) -> dict[str, object]:
        if not r.consent:
            raise ValueError("consent_required")
        key = hashlib.sha256(str(r.email).lower().encode()).hexdigest()
        token = secrets.token_urlsafe(24)
        self._pending[token] = key
        return {"status": "confirmation_pending", "confirmation_token": token}

    def confirm(self, token: str) -> dict[str, str]:
        key = self._pending.pop(token, None)
        if key is None:
            return {"status": "not_found"}
        self._active.add(key)
        return {"status": "subscribed"}

    def unsubscribe(self, email: str) -> dict[str, str]:
        self._active.discard(hashlib.sha256(email.lower().encode()).hexdigest())
        return {"status": "unsubscribed"}
