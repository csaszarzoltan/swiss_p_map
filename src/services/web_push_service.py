"""Anonymous Web Push subscription and watch-alert deduplication (SPEC-060)."""

from pydantic import BaseModel, Field


class PushSubscription(BaseModel):
    endpoint: str = Field(pattern=r"^https://")
    p256dh: str
    auth: str


class WatchAlert(BaseModel):
    subscription_endpoint: str
    zone_id: str
    event_id: str
    title: str


class WebPushService:
    def __init__(self) -> None:
        self._subscriptions: set[str] = set()
        self._sent: set[tuple[str, str]] = set()

    def subscribe(self, s: PushSubscription) -> dict[str, str]:
        self._subscriptions.add(s.endpoint)
        return {"status": "subscribed"}

    def alert(self, a: WatchAlert) -> dict[str, str]:
        key = (a.subscription_endpoint, a.event_id)
        if a.subscription_endpoint not in self._subscriptions:
            return {"status": "subscription_not_found"}
        if key in self._sent:
            return {"status": "deduplicated"}
        self._sent.add(key)
        return {"status": "queued"}
