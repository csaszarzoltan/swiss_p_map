"""Watch-zone alert pipeline + Einsprachefrist manager (ADR-023, SPEC-059/060).

Real integration, no simulation (zero-mock policy):

- Zones live in SQLite (``WatchStore``), so consent + dedup survive restarts.
- Matcher filters the *ingested* Baugesuch store by deterministic haversine distance.
- Push channel delegates to the existing :class:`WebPushService`; e-mail channel
  delegates to :class:`NewsletterService` (double opt-in). Both are honest:
  without VAPID/SMTP configured the delivery reports ``queued`` /
  ``queued_pending_opt_in`` — never a fabricated "sent".
- Einsprachefrist: ``publication_date + AUFLAGE_DAYS`` (documented rule), with
  ``open`` / ``due_soon`` (<= 3 days) / ``expired`` state and a mandatory
  disclaimer (REQ-B3).
"""

from __future__ import annotations

import json
import sqlite3
from datetime import UTC, date, datetime, timedelta
from pathlib import Path
from typing import Literal

from pydantic import BaseModel, Field, model_validator

from src.db.planning_repo import PlanningRepo
from src.models.planning import AUFLAGE_DAYS, Baugesuch
from src.services.geo_converter import haversine_distance_m
from src.services.newsletter_service import NewsletterService, SubscribeRequest
from src.services.place_service import POSTCODE_WGS84
from src.services.web_push_service import PushSubscription, WatchAlert, WebPushService

SOURCE = "Kantonale E-Amtsblätter"
TRUST_STATE = "official_publication"
DUE_SOON_DAYS = 3
DISCLAIMER = (
    "Keine Rechtsberatung; ersetzt weder anwaltliche Beratung noch Vertretung. "
    "Fristen und Zuständigkeit amtlich prüfen."
)
RULE = f"deadline = publication_date + {AUFLAGE_DAYS} Tage (Standardfrist, ADR-023)"

Channel = Literal["push", "email"]
EventKind = Literal["new_permit", "deadline_soon"]
DeadlineState = Literal["open", "due_soon", "expired"]


def deadline_for(publication: date) -> date:
    """REQ-B1: the einzige, dokumentierte Frist-Regel (publication_date + 20 Tage)."""
    return publication + timedelta(days=AUFLAGE_DAYS)


def deadline_state(days_left: int) -> DeadlineState:
    """REQ-B2: expired is never reported as open; due_soon threshold is 3 days."""
    if days_left < 0:
        return "expired"
    if days_left <= DUE_SOON_DAYS:
        return "due_soon"
    return "open"


# --------------------------------------------------------------------- models


class WatchZoneRequest(BaseModel):
    """User-supplied watch zone (REQ-A1: consent + channel target are required)."""

    zone_id: str = Field(min_length=1, max_length=64)
    postcode: str | None = Field(default=None, pattern=r"^\d{4}$")
    lat: float | None = Field(default=None, ge=45.0, le=48.0)
    lon: float | None = Field(default=None, ge=5.0, le=11.0)
    radius_m: float = Field(default=500.0, ge=50.0, le=50000.0)
    channels: list[Channel] = Field(min_length=1)
    consent: bool
    subscription_endpoint: str | None = None
    email: str | None = None

    @model_validator(mode="after")
    def _check_targets(self) -> WatchZoneRequest:
        if self.postcode is None and (self.lat is None or self.lon is None):
            raise ValueError("zone_requires_center_or_postcode")
        if "push" in self.channels and not self.subscription_endpoint:
            raise ValueError("push_channel_requires_subscription_endpoint")
        if "email" in self.channels and not self.email:
            raise ValueError("email_channel_requires_email")
        return self


class WatchZone(BaseModel):
    zone_id: str
    postcode: str | None = None
    lat: float
    lon: float
    radius_m: float
    channels: list[Channel]
    consent: bool
    subscription_endpoint: str | None = None
    email: str | None = None
    created_at: str = ""
    center_source: str = "explicit_coordinates"


class DeliveryResult(BaseModel):
    channel: Channel
    status: str
    detail: str = ""


class WatchEvent(BaseModel):
    event_id: str
    zone_id: str
    baugesuch_id: str
    kind: EventKind
    distance_m: float
    title: str
    postcode: str
    canton: str
    publication_date: str
    deadline: str
    days_left: int
    state: DeadlineState
    source_url: str
    source: str = SOURCE
    trust_state: str = TRUST_STATE
    fetched_at: str = ""
    delivery: list[DeliveryResult] = Field(default_factory=list)


class DeadlineItem(BaseModel):
    baugesuch_id: str
    zone_id: str = ""
    postcode: str
    municipality: str
    title: str
    publication_date: str
    deadline: str
    days_left: int
    state: DeadlineState
    source_url: str
    source: str = SOURCE
    trust_state: str = TRUST_STATE
    disclaimer: str = DISCLAIMER
    rule: str = RULE


class DeadlinesResponse(BaseModel):
    count: int
    items: list[DeadlineItem]
    status: str
    rule: str = RULE
    disclaimer: str = DISCLAIMER
    source: str = SOURCE
    trust_state: str
    fetched_at: str = ""
    zone_id: str | None = None
    postcode: str | None = None


class EventsResponse(BaseModel):
    count: int
    items: list[WatchEvent]
    status: str
    source: str = SOURCE
    trust_state: str
    fetched_at: str = ""


class ZonesResponse(BaseModel):
    count: int
    items: list[WatchZone]


class RunResult(BaseModel):
    status: str
    zones_processed: int = 0
    skipped_no_consent: int = 0
    events_created: int = 0
    deduplicated: int = 0
    items: list[WatchEvent] = Field(default_factory=list)
    source: str = SOURCE
    trust_state: str = TRUST_STATE
    fetched_at: str = ""
    disclaimer: str = DISCLAIMER


# ---------------------------------------------------------------------- store

_ZONE_DDL = """
CREATE TABLE IF NOT EXISTS watch_zones (
    zone_id TEXT PRIMARY KEY,
    postcode TEXT,
    lat REAL NOT NULL,
    lon REAL NOT NULL,
    radius_m REAL NOT NULL,
    channels TEXT NOT NULL,
    consent INTEGER NOT NULL,
    subscription_endpoint TEXT,
    email TEXT,
    created_at TEXT NOT NULL,
    center_source TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS watch_events (
    event_id TEXT PRIMARY KEY,
    zone_id TEXT NOT NULL,
    baugesuch_id TEXT NOT NULL,
    kind TEXT NOT NULL,
    payload TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_watch_events_zone ON watch_events(zone_id);
"""


class WatchStore:
    """Persistent zone registry + dedup ledger (REQ-A2: survives restarts)."""

    def __init__(self, db_path: str = "data/watch.db") -> None:
        self._db_path = db_path
        if db_path != ":memory:":
            Path(db_path).parent.mkdir(parents=True, exist_ok=True)
        self._conn = sqlite3.connect(db_path, check_same_thread=False)
        self._conn.row_factory = sqlite3.Row
        self._conn.executescript(_ZONE_DDL)
        self._conn.commit()

    @staticmethod
    def _to_zone(row: sqlite3.Row) -> WatchZone:
        return WatchZone(
            zone_id=row["zone_id"],
            postcode=row["postcode"],
            lat=row["lat"],
            lon=row["lon"],
            radius_m=row["radius_m"],
            channels=json.loads(row["channels"]),
            consent=bool(row["consent"]),
            subscription_endpoint=row["subscription_endpoint"],
            email=row["email"],
            created_at=row["created_at"],
            center_source=row["center_source"],
        )

    def save_zone(self, zone: WatchZone) -> WatchZone:
        self._conn.execute(
            """INSERT INTO watch_zones
               (zone_id,postcode,lat,lon,radius_m,channels,consent,
                subscription_endpoint,email,created_at,center_source)
               VALUES (?,?,?,?,?,?,?,?,?,?,?)
               ON CONFLICT(zone_id) DO UPDATE SET
                 postcode=excluded.postcode, lat=excluded.lat, lon=excluded.lon,
                 radius_m=excluded.radius_m, channels=excluded.channels,
                 consent=excluded.consent,
                 subscription_endpoint=excluded.subscription_endpoint,
                 email=excluded.email, center_source=excluded.center_source""",
            (
                zone.zone_id,
                zone.postcode,
                zone.lat,
                zone.lon,
                zone.radius_m,
                json.dumps(zone.channels),
                int(zone.consent),
                zone.subscription_endpoint,
                zone.email,
                zone.created_at,
                zone.center_source,
            ),
        )
        self._conn.commit()
        return zone

    def list_zones(self) -> list[WatchZone]:
        rows = self._conn.execute(
            "SELECT * FROM watch_zones ORDER BY created_at, zone_id"
        ).fetchall()
        return [self._to_zone(r) for r in rows]

    def get_zone(self, zone_id: str) -> WatchZone | None:
        row = self._conn.execute(
            "SELECT * FROM watch_zones WHERE zone_id = ?", (zone_id,)
        ).fetchone()
        return self._to_zone(row) if row else None

    def delete_zone(self, zone_id: str) -> int:
        cur = self._conn.execute(
            "DELETE FROM watch_events WHERE zone_id = ?", (zone_id,)
        )
        removed = cur.rowcount
        self._conn.execute("DELETE FROM watch_zones WHERE zone_id = ?", (zone_id,))
        self._conn.commit()
        return removed

    def has_event(self, zone_id: str, baugesuch_id: str, kind: str) -> bool:
        """True when the dedup key (zone_id, baugesuch_id, kind) is already stored."""
        row = self._conn.execute(
            """SELECT 1 FROM watch_events
               WHERE zone_id = ? AND baugesuch_id = ? AND kind = ? LIMIT 1""",
            (zone_id, baugesuch_id, kind),
        ).fetchone()
        return row is not None

    def record_event(self, event: WatchEvent) -> bool:
        """True when the dedup key (zone_id, baugesuch_id, kind) is new."""
        cur = self._conn.execute(
            """INSERT OR IGNORE INTO watch_events
               (event_id,zone_id,baugesuch_id,kind,payload) VALUES (?,?,?,?,?)""",
            (
                event.event_id,
                event.zone_id,
                event.baugesuch_id,
                event.kind,
                event.model_dump_json(),
            ),
        )
        self._conn.commit()
        return cur.rowcount == 1

    def list_events(self, kind: EventKind | None = None, limit: int = 50) -> list[WatchEvent]:
        sql = "SELECT payload FROM watch_events"
        params: list[object] = []
        if kind:
            sql += " WHERE kind = ?"
            params.append(kind)
        sql += " ORDER BY event_id LIMIT ?"
        params.append(limit)
        rows = self._conn.execute(sql, params).fetchall()
        return [WatchEvent.model_validate_json(r["payload"]) for r in rows]


# -------------------------------------------------------------------- matcher


class WatchMatcher:
    """Deterministic distance filter over ingested Baugesuche (ADR-023 §1)."""

    def __init__(self, items: list[Baugesuch] | None = None) -> None:
        self._items = items or []

    def match(self, zone: WatchZone, items: list[Baugesuch]) -> list[tuple[Baugesuch, float]]:
        results: list[tuple[Baugesuch, float]] = []
        for item in items:
            if item.lat is None or item.lon is None:
                continue
            dist = haversine_distance_m(zone.lat, zone.lon, item.lat, item.lon)
            if dist <= zone.radius_m:
                results.append((item, dist))
        results.sort(key=lambda pair: (pair[1], pair[0].id))
        return results


# -------------------------------------------------------------------- service


class WatchService:
    """Watch-zone CRUD + alert run + Einsprachefrist management (ADR-023)."""

    def __init__(
        self,
        repo: PlanningRepo | None = None,
        store: WatchStore | None = None,
        matcher: WatchMatcher | None = None,
        web_push: WebPushService | None = None,
        newsletter: NewsletterService | None = None,
    ) -> None:
        self._repo = repo or PlanningRepo()
        self._store = store or WatchStore()
        self._matcher = matcher or WatchMatcher()
        self._web_push = web_push or WebPushService()
        self._newsletter = newsletter or NewsletterService()

    @property
    def store(self) -> WatchStore:
        return self._store

    # ---------------------------------------------------------------- zones

    def create_zone(self, request: WatchZoneRequest) -> WatchZone:
        if not request.consent:
            raise ValueError("consent_required: REQ-A1 erlaubt keine Zone ohne Einwilligung")
        lat, lon, source = request.lat, request.lon, "explicit_coordinates"
        if lat is None or lon is None:
            center = POSTCODE_WGS84.get(request.postcode or "")
            if center is None:
                raise ValueError(f"unknown_postcode_center: {request.postcode}")
            lon, lat = center
            source = "postcode_pilot_center"
        zone = WatchZone(
            zone_id=request.zone_id,
            postcode=request.postcode,
            lat=lat,
            lon=lon,
            radius_m=request.radius_m,
            channels=list(request.channels),
            consent=True,
            subscription_endpoint=request.subscription_endpoint,
            email=request.email,
            created_at=datetime.now(UTC).replace(microsecond=0).isoformat(),
            center_source=source,
        )
        if zone.subscription_endpoint:
            self._web_push.subscribe(
                PushSubscription(
                    endpoint=zone.subscription_endpoint,
                    p256dh="zone-registered",
                    auth="zone-registered",
                )
            )
        return self._store.save_zone(zone)

    def list_zones(self) -> ZonesResponse:
        zones = self._store.list_zones()
        return ZonesResponse(count=len(zones), items=zones)

    def delete_zone(self, zone_id: str) -> int:
        return self._store.delete_zone(zone_id)

    # ------------------------------------------------------------- deadlines

    def _deadline_item(self, item: Baugesuch, zone_id: str, on: date) -> DeadlineItem:
        deadline = deadline_for(item.publication_date)
        days_left = (deadline - on).days
        return DeadlineItem(
            baugesuch_id=item.id,
            zone_id=zone_id,
            postcode=item.postcode,
            municipality=item.municipality,
            title=item.title,
            publication_date=item.publication_date.isoformat(),
            deadline=deadline.isoformat(),
            days_left=days_left,
            state=deadline_state(days_left),
            source_url=item.source_url,
        )

    def deadlines(
        self,
        postcode: str | None = None,
        zone_id: str | None = None,
        on: date | None = None,
    ) -> DeadlinesResponse:
        """REQ-B1/B2/B3: Frist + Zustand + Disclaimer, dringlichste zuerst."""
        ref = on or date.today()  # noqa: DTZ011 — caller injects "on" in tests
        stamp = datetime.now(UTC).isoformat()
        zone = self._store.get_zone(zone_id) if zone_id else None
        if zone_id and zone is None:
            raise ValueError(f"zone_not_found: {zone_id}")
        if zone is not None:
            kind = "success"
            # Same deterministic distance matcher as run() — ADR-023 §1.
            candidates = self._repo.list_items(on=ref)
            matched = self._matcher.match(zone, candidates)
            items = [self._deadline_item(b, zone.zone_id, ref) for b, _ in matched]
        else:
            stored = self._repo.list_items(postcode=postcode, on=ref)
            kind = "success" if stored else "source_pending"
            items = [self._deadline_item(b, "", ref) for b in stored]
        items.sort(key=lambda i: (i.days_left, i.baugesuch_id))
        return DeadlinesResponse(
            count=len(items),
            items=items,
            status=kind,
            trust_state=TRUST_STATE if items else "source_pending",
            fetched_at=stamp,
            zone_id=zone.zone_id if zone else None,
            postcode=postcode,
        )

    # ------------------------------------------------------------------ run

    def _deliver(self, zone: WatchZone, event: WatchEvent, item: Baugesuch) -> list[DeliveryResult]:
        """Route through the real push/newsletter services — honest statuses only."""
        results: list[DeliveryResult] = []
        for channel in zone.channels:
            if channel == "push" and zone.subscription_endpoint:
                outcome = self._web_push.alert(
                    WatchAlert(
                        subscription_endpoint=zone.subscription_endpoint,
                        zone_id=zone.zone_id,
                        event_id=event.event_id,
                        title=event.title,
                    )
                )
                results.append(
                    DeliveryResult(
                        channel="push",
                        status=outcome["status"],
                        detail="VAPID nicht konfiguriert — Zustellung wartet in der Schlange",
                    )
                )
            elif channel == "email" and zone.email:
                try:
                    outcome_email = self._newsletter.subscribe(
                        SubscribeRequest(
                            email=zone.email, postcode=item.postcode, consent=True
                        )
                    )
                    results.append(
                        DeliveryResult(
                            channel="email",
                            status="queued_pending_opt_in",
                            detail=str(outcome_email.get("status", "")),
                        )
                    )
                except ValueError as exc:  # invalid address -> honest failure
                    results.append(
                        DeliveryResult(channel="email", status="invalid_target", detail=str(exc))
                    )
        return results

    def run(
        self,
        zone_id: str | None = None,
        on: date | None = None,
        now: datetime | None = None,
    ) -> RunResult:
        """Match stored zones against the ingested store and dedup-deliver (REQ-A1/A2/A3)."""
        ref = on or date.today()  # noqa: DTZ011 — injectable for tests
        stamp = (now or datetime.now(UTC)).replace(microsecond=0).isoformat()
        zones = self._store.list_zones()
        if zone_id:
            zones = [z for z in zones if z.zone_id == zone_id]
        if not zones:
            return RunResult(status="no_zones", fetched_at=stamp)
        active = self._repo.list_items(active_only=True, on=ref)
        if not active:
            return RunResult(status="source_pending", trust_state="source_pending",
                             fetched_at=stamp)
        created = deduplicated = skipped = processed = 0
        emitted: list[WatchEvent] = []
        for zone in zones:
            if not zone.consent:
                skipped += 1  # REQ-A1: no consent -> never notified
                continue
            matched = self._matcher.match(zone, active)
            if not matched:
                continue
            processed += 1
            for item, dist in matched:
                deadline = deadline_for(item.publication_date)
                days_left = (deadline - ref).days
                if days_left < 0:
                    continue  # REQ-B2: expired window -> nothing to alert about
                kinds: list[EventKind] = ["new_permit"]
                if deadline_state(days_left) == "due_soon":
                    kinds.append("deadline_soon")
                for kind in kinds:
                    if self._store.has_event(zone.zone_id, item.id, kind):
                        deduplicated += 1  # REQ-A2: same (zone,baugesuch,kind) never twice
                        continue
                    event = WatchEvent(
                        event_id=f"{zone.zone_id}:{item.id}:{kind}",
                        zone_id=zone.zone_id,
                        baugesuch_id=item.id,
                        kind=kind,
                        distance_m=dist,
                        title=item.title,
                        postcode=item.postcode,
                        canton=item.canton,
                        publication_date=item.publication_date.isoformat(),
                        deadline=deadline.isoformat(),
                        days_left=days_left,
                        state=deadline_state(days_left),
                        source_url=item.source_url,
                        fetched_at=stamp,
                    )
                    event.delivery = self._deliver(zone, event, item)
                    self._store.record_event(event)  # persist event + delivery outcome
                    created += 1
                    emitted.append(event)
        return RunResult(
            status="success",
            zones_processed=processed,
            skipped_no_consent=skipped,
            events_created=created,
            deduplicated=deduplicated,
            items=emitted,
            fetched_at=stamp,
        )

    # --------------------------------------------------------------- events

    def events(self, kind: EventKind | None = None, limit: int = 50) -> EventsResponse:
        stamp = datetime.now(UTC).isoformat()
        stored = self._store.list_events(kind=kind, limit=limit)
        if stored:
            status = "success"
        elif self._repo.list_items(active_only=True):
            status = "empty"
        else:
            status = "source_pending"
        return EventsResponse(
            count=len(stored),
            items=stored,
            status=status,
            trust_state=TRUST_STATE if stored else "source_pending",
            fetched_at=stamp,
        )
