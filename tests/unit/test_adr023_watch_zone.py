"""ADR-023 backend tests: watch-zone alert pipeline + Einsprachefrist manager.

TDD RED -> GREEN for kanban task t_9f502c9a. Traceability to
`docs/decisions/ADR-023-watch-zone-alert-pipeline.md`:

- REQ-A1: alert only for a user-defined zone and only with consent.
- REQ-A2: the same event is never delivered twice (persistent dedup key).
- REQ-A3: every event carries source / fetched_at / trust_state.
- REQ-B1: the objection deadline derives from the publication date (documented rule).
- REQ-B2: an expired deadline can never surface as open; due_soon threshold 3 days.
- REQ-B3: deadline information is not legal advice -> disclaimer mandatory.
"""

from __future__ import annotations

from datetime import date, timedelta
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from src.db.planning_repo import PlanningRepo
from src.main import app
from src.models.planning import AUFLAGE_DAYS, Baugesuch
from src.services.geo_converter import haversine_distance_m
from src.services.place_service import POSTCODE_WGS84
from src.services.watch_service import (
    DISCLAIMER,
    DUE_SOON_DAYS,
    WatchMatcher,
    WatchService,
    WatchStore,
    WatchZone,
    WatchZoneRequest,
)

BASE_DAY = date(2026, 9, 24)
ZRH_LON, ZRH_LAT = POSTCODE_WGS84["8004"]
BERN_LON, BERN_LAT = POSTCODE_WGS84["3011"]

c = TestClient(app)


def _bg(
    bid: str,
    published: date,
    lat: float,
    lon: float,
    postcode: str = "8004",
    canton: str = "ZH",
    auflage_end: date | None = None,
) -> Baugesuch:
    return Baugesuch(
        id=bid,
        title=f"{bid} Neubau Wohnhaus (Testfixture)",
        municipality="Zürich",
        postcode=postcode,
        canton=canton,
        publication_date=published,
        expiration_date=published + timedelta(days=360),
        auflage_start=published,
        auflage_end=auflage_end or published + timedelta(days=AUFLAGE_DAYS),
        source_url=f"https://amtsblattportal.ch/api/v1/publications/{bid}/xml",
        lat=lat,
        lon=lon,
    )


def _zone_request(
    zone_id: str = "z-1",
    lat: float = ZRH_LAT,
    lon: float = ZRH_LON,
    radius_m: float = 500.0,
    channels: tuple[str, ...] = ("push",),
    consent: bool = True,
) -> WatchZoneRequest:
    return WatchZoneRequest(
        zone_id=zone_id,
        lat=lat,
        lon=lon,
        radius_m=radius_m,
        channels=list(channels),  # type: ignore[arg-type]
        consent=consent,
        subscription_endpoint="https://push.example.test/ep-1" if "push" in channels else None,
        email="resident@example.ch" if "email" in channels else None,
    )


def _service(
    items: list[Baugesuch] | None = None,
    store: WatchStore | None = None,
) -> WatchService:
    repo = PlanningRepo(":memory:")
    if items:
        repo.upsert_many(items)
    return WatchService(repo=repo, store=store or WatchStore(":memory:"))


# ------------------------------------------------------------------ REQ-A1


def test_adr023_req_a1_consent_required_for_zone_creation() -> None:
    svc = _service()
    with pytest.raises(ValueError, match="consent"):
        svc.create_zone(_zone_request(consent=False))


def test_adr023_req_a1_consent_missing_api_returns_400() -> None:
    resp = c.post(
        "/api/v1/watch/zones",
        json={
            "zone_id": "z-no-consent",
            "lat": ZRH_LAT,
            "lon": ZRH_LON,
            "radius_m": 500,
            "channels": ["push"],
            "consent": False,
            "subscription_endpoint": "https://push.example.test/ep-x",
        },
    )
    assert resp.status_code == 400
    assert "consent" in resp.json()["detail"]


def test_adr023_req_a1_run_skips_stored_zone_without_consent() -> None:
    svc = _service([_bg("bg-near", BASE_DAY - timedelta(days=2), ZRH_LAT, ZRH_LON)])
    legacy = WatchZone(
        zone_id="z-legacy",
        lat=ZRH_LAT,
        lon=ZRH_LON,
        radius_m=500.0,
        channels=["push"],
        consent=False,
        created_at="2026-09-01T00:00:00+00:00",
    )
    svc.store.save_zone(legacy)
    result = svc.run(on=BASE_DAY)
    assert result.skipped_no_consent == 1
    assert result.events_created == 0
    assert result.zones_processed == 0
    assert svc.events().count == 0


def test_adr023_req_a1_run_only_matches_its_own_zone() -> None:
    svc = _service(
        [
            _bg("bg-zrh-near", BASE_DAY - timedelta(days=2), ZRH_LAT, ZRH_LON),
            _bg("bg-zrh-far", BASE_DAY - timedelta(days=2), 47.390, 8.534),
            _bg(
                "bg-bern",
                BASE_DAY - timedelta(days=2),
                BERN_LAT,
                BERN_LON,
                postcode="3011",
                canton="BE",
            ),
        ]
    )
    svc.create_zone(_zone_request(zone_id="z-zrh", radius_m=500.0))
    result = svc.run(on=BASE_DAY)
    assert {e.baugesuch_id for e in result.items} == {"bg-zrh-near"}
    assert all(e.zone_id == "z-zrh" for e in result.items)


def test_adr023_req_a1_postcode_only_zone_resolves_pilot_center() -> None:
    svc = _service([_bg("bg-near", BASE_DAY - timedelta(days=2), ZRH_LAT, ZRH_LON)])
    zone = svc.create_zone(
        WatchZoneRequest(
            zone_id="z-postcode",
            postcode="8004",
            radius_m=500.0,
            channels=["push"],
            consent=True,
            subscription_endpoint="https://push.example.test/ep-2",
        )
    )
    assert (zone.lat, zone.lon) == (ZRH_LAT, ZRH_LON)
    assert zone.center_source == "postcode_pilot_center"


def test_adr023_req_a1_unknown_postcode_without_center_is_rejected() -> None:
    svc = _service()
    with pytest.raises(ValueError, match="unknown_postcode_center"):
        svc.create_zone(
            WatchZoneRequest(
                zone_id="z-unknown",
                postcode="9999",
                radius_m=500.0,
                channels=["push"],
                consent=True,
                subscription_endpoint="https://push.example.test/ep-3",
            )
        )


def test_adr023_req_a1_channel_requires_its_delivery_target() -> None:
    svc = _service()
    with pytest.raises(ValueError, match="push_channel_requires"):
        svc.create_zone(
            WatchZoneRequest(
                zone_id="z-no-push-target",
                lat=ZRH_LAT,
                lon=ZRH_LON,
                radius_m=500.0,
                channels=["push"],
                consent=True,
            )
        )
    with pytest.raises(ValueError, match="email_channel_requires"):
        svc.create_zone(
            WatchZoneRequest(
                zone_id="z-no-email-target",
                lat=ZRH_LAT,
                lon=ZRH_LON,
                radius_m=500.0,
                channels=["email"],
                consent=True,
            )
        )


# ------------------------------------------------------------------ REQ-A2


def test_adr023_req_a2_second_run_is_deduplicated() -> None:
    svc = _service([_bg("bg-near", BASE_DAY - timedelta(days=2), ZRH_LAT, ZRH_LON)])
    svc.create_zone(_zone_request(zone_id="z-dedup"))
    first = svc.run(on=BASE_DAY)
    assert first.events_created >= 1
    assert first.deduplicated == 0
    second = svc.run(on=BASE_DAY)
    assert second.events_created == 0
    assert second.deduplicated == first.events_created
    assert svc.events().count == first.events_created


def test_adr023_req_a2_dedup_key_survives_service_restart(tmp_path: Path) -> None:
    db = tmp_path / "watch.db"
    items = [_bg("bg-near", BASE_DAY - timedelta(days=2), ZRH_LAT, ZRH_LON)]
    repo = PlanningRepo(":memory:")
    repo.upsert_many(items)

    first_svc = WatchService(repo=repo, store=WatchStore(str(db)))
    first_svc.create_zone(_zone_request(zone_id="z-restart"))
    first = first_svc.run(on=BASE_DAY)
    assert first.events_created >= 1

    # New process/instance on the same SQLite file: dedup must persist.
    reloaded = WatchService(repo=repo, store=WatchStore(str(db)))
    assert reloaded.events().count == first.events_created
    again = reloaded.run(on=BASE_DAY)
    assert again.events_created == 0
    assert again.deduplicated == first.events_created


def test_adr023_req_a2_kind_is_part_of_the_dedup_key() -> None:
    published = BASE_DAY - timedelta(days=AUFLAGE_DAYS - 2)  # days_left == 2 -> due_soon
    svc = _service([_bg("bg-due", published, ZRH_LAT, ZRH_LON)])
    svc.create_zone(_zone_request(zone_id="z-kinds"))
    result = svc.run(on=BASE_DAY)
    kinds = sorted(e.kind for e in result.items)
    assert kinds == ["deadline_soon", "new_permit"]
    assert len({e.event_id for e in result.items}) == 2
    repeat = svc.run(on=BASE_DAY)
    assert repeat.events_created == 0
    assert repeat.deduplicated == 2


def test_adr023_req_a2_expired_permit_produces_no_new_event() -> None:
    published = BASE_DAY - timedelta(days=AUFLAGE_DAYS + 1)  # deadline yesterday
    svc = _service(
        [
            _bg(
                "bg-expired",
                published,
                ZRH_LAT,
                ZRH_LON,
                auflage_end=BASE_DAY + timedelta(days=5),
            )
        ]
    )
    svc.create_zone(_zone_request(zone_id="z-expired"))
    result = svc.run(on=BASE_DAY)
    assert result.events_created == 0
    assert result.items == []


def test_adr023_req_a2_matcher_is_deterministic_and_radius_bounded() -> None:
    matcher = WatchMatcher()
    items = [
        _bg("bg-far", BASE_DAY, 47.3830, 8.5340),
        _bg("bg-near", BASE_DAY, ZRH_LAT, ZRH_LON),
        _bg("bg-mid", BASE_DAY, 47.3790, 8.5340),
        _bg("bg-nogeo", BASE_DAY, ZRH_LAT, ZRH_LON),
    ]
    items[-1] = items[-1].model_copy(update={"lat": None, "lon": None})
    zone = WatchZone(
        zone_id="z-order",
        lat=ZRH_LAT,
        lon=ZRH_LON,
        radius_m=500.0,
        channels=["push"],
        consent=True,
        created_at="2026-09-01T00:00:00+00:00",
    )
    matched = matcher.match(zone, items)
    ids = [b.id for b, _ in matched]
    assert "bg-nogeo" not in ids
    distances = [d for _, d in matched]
    assert distances == sorted(distances)
    assert all(d <= 500.0 for d in distances)
    assert ids == ["bg-near", "bg-mid"]
    assert haversine_distance_m(ZRH_LAT, ZRH_LON, 47.3830, 8.5340) > 500.0


def test_adr023_req_a2_matcher_breaks_ties_by_id() -> None:
    items = [
        _bg("bg-b", BASE_DAY, ZRH_LAT, ZRH_LON),
        _bg("bg-a", BASE_DAY, ZRH_LAT, ZRH_LON),
    ]
    zone = WatchZone(
        zone_id="z-tie",
        lat=ZRH_LAT,
        lon=ZRH_LON,
        radius_m=500.0,
        channels=["push"],
        consent=True,
        created_at="2026-09-01T00:00:00+00:00",
    )
    assert [b.id for b, _ in WatchMatcher().match(zone, items)] == ["bg-a", "bg-b"]


# ------------------------------------------------------------------ REQ-A3


def test_adr023_req_a3_events_carry_source_fetched_at_trust_state() -> None:
    svc = _service([_bg("bg-near", BASE_DAY - timedelta(days=2), ZRH_LAT, ZRH_LON)])
    svc.create_zone(_zone_request(zone_id="z-prov"))
    result = svc.run(on=BASE_DAY)
    assert result.items
    for event in result.items:
        assert event.source == "Kantonale E-Amtsblätter"
        assert event.trust_state == "official_publication"
        assert event.fetched_at
        assert event.source_url.startswith("https://")
        assert event.distance_m >= 0
    assert result.fetched_at


def test_adr023_req_a3_push_delivery_is_queued_never_falsely_sent() -> None:
    svc = _service([_bg("bg-near", BASE_DAY - timedelta(days=2), ZRH_LAT, ZRH_LON)])
    svc.create_zone(_zone_request(zone_id="z-channels", channels=("push", "email")))
    result = svc.run(on=BASE_DAY)
    statuses = {d.channel: d.status for d in result.items[0].delivery}
    assert statuses == {"push": "queued", "email": "queued_pending_opt_in"}


def test_adr023_req_a3_empty_store_is_source_pending_not_fabricated() -> None:
    svc = _service()
    svc.create_zone(_zone_request(zone_id="z-empty"))
    result = svc.run(on=BASE_DAY)
    assert result.status == "source_pending"
    assert result.trust_state == "source_pending"
    assert result.events_created == 0
    events = svc.events()
    assert events.count == 0
    assert events.status == "source_pending"


# ------------------------------------------------------------------ REQ-B1


def test_adr023_req_b1_deadline_is_publication_plus_documented_rule() -> None:
    published = BASE_DAY - timedelta(days=5)
    svc = _service([_bg("bg-rule", published, ZRH_LAT, ZRH_LON)])
    svc.create_zone(_zone_request(zone_id="z-rule"))
    deadlines = svc.deadlines(zone_id="z-rule", on=BASE_DAY)
    assert deadlines.count == 1
    item = deadlines.items[0]
    assert item.deadline == (published + timedelta(days=AUFLAGE_DAYS)).isoformat()
    assert item.publication_date == published.isoformat()
    assert item.days_left == AUFLAGE_DAYS - 5
    assert f"publication_date + {AUFLAGE_DAYS}" in item.rule
    assert item.source == "Kantonale E-Amtsblätter"


def test_adr023_req_b1_zone_deadlines_use_distance_matcher_like_run() -> None:
    """ADR-023 §1: a zone-scoped deadline list must use the same distance matcher as run()."""
    svc = _service(
        [
            _bg("bg-in-radius", BASE_DAY - timedelta(days=4), ZRH_LAT, ZRH_LON),
            _bg("bg-outside", BASE_DAY - timedelta(days=4), 47.3830, 8.5340),
        ]
    )
    svc.create_zone(_zone_request(zone_id="z-consistent", radius_m=500.0))
    run_ids = {e.baugesuch_id for e in svc.run(on=BASE_DAY).items}
    deadline_ids = {
        i.baugesuch_id for i in svc.deadlines(zone_id="z-consistent", on=BASE_DAY).items
    }
    assert run_ids == {"bg-in-radius"}
    assert deadline_ids == run_ids


def test_adr023_req_b1_deadlines_api_contract() -> None:
    resp = c.get("/api/v1/watch/deadlines?postcode=8004")
    assert resp.status_code == 200
    body = resp.json()
    for key in ("count", "items", "status", "rule", "disclaimer", "source",
                "trust_state", "fetched_at"):
        assert key in body, f"missing {key}"
    assert body["count"] >= 1
    for item in body["items"]:
        published = date.fromisoformat(item["publication_date"])
        assert item["deadline"] == (
            published + timedelta(days=AUFLAGE_DAYS)
        ).isoformat()
        assert item["state"] in {"open", "due_soon", "expired"}


# ------------------------------------------------------------------ REQ-B2


@pytest.mark.parametrize(
    ("days_left", "expected_state"),
    [
        (15, "open"),
        (DUE_SOON_DAYS + 1, "open"),
        (DUE_SOON_DAYS, "due_soon"),
        (1, "due_soon"),
        (0, "due_soon"),
        (-1, "expired"),
    ],
)
def test_adr023_req_b2_deadline_state_machine(days_left: int, expected_state: str) -> None:
    published = BASE_DAY - timedelta(days=AUFLAGE_DAYS - days_left)
    svc = _service(
        [
            _bg(
                "bg-state",
                published,
                ZRH_LAT,
                ZRH_LON,
                auflage_end=BASE_DAY + timedelta(days=10),
            )
        ]
    )
    svc.create_zone(_zone_request(zone_id="z-state"))
    item = svc.deadlines(zone_id="z-state", on=BASE_DAY).items[0]
    assert item.days_left == days_left
    assert item.state == expected_state
    assert item.deadline == (published + timedelta(days=AUFLAGE_DAYS)).isoformat()


def test_adr023_req_b2_expired_deadline_never_open() -> None:
    published = BASE_DAY - timedelta(days=AUFLAGE_DAYS + 30)
    svc = _service(
        [
            _bg(
                "bg-late",
                published,
                ZRH_LAT,
                ZRH_LON,
                auflage_end=BASE_DAY + timedelta(days=10),
            )
        ]
    )
    svc.create_zone(_zone_request(zone_id="z-late"))
    item = svc.deadlines(zone_id="z-late", on=BASE_DAY).items[0]
    assert item.days_left < 0
    assert item.state == "expired"
    assert "open" not in item.state


def test_adr023_req_b2_deadlines_sorted_most_urgent_first() -> None:
    svc = _service(
        [
            _bg("bg-open", BASE_DAY - timedelta(days=2), ZRH_LAT, ZRH_LON),
            _bg("bg-due", BASE_DAY - timedelta(days=19), ZRH_LAT, ZRH_LON),
        ]
    )
    svc.create_zone(_zone_request(zone_id="z-sort"))
    items = svc.deadlines(zone_id="z-sort", on=BASE_DAY).items
    assert [i.baugesuch_id for i in items] == ["bg-due", "bg-open"]
    assert [i.days_left for i in items] == sorted(i.days_left for i in items)


# ------------------------------------------------------------------ REQ-B3


def test_adr023_req_b3_disclaimer_is_mandatory() -> None:
    published = BASE_DAY - timedelta(days=4)
    svc = _service([_bg("bg-law", published, ZRH_LAT, ZRH_LON)])
    svc.create_zone(_zone_request(zone_id="z-law"))
    deadline_item = svc.deadlines(zone_id="z-law", on=BASE_DAY).items[0]
    assert deadline_item.disclaimer == DISCLAIMER
    assert "Keine Rechtsberatung" in deadline_item.disclaimer
    response = svc.deadlines(zone_id="z-law", on=BASE_DAY)
    assert response.disclaimer == DISCLAIMER
    assert "Keine Rechtsberatung" in response.disclaimer


def test_adr023_req_b3_deadlines_api_exposes_disclaimer() -> None:
    body = c.get("/api/v1/watch/deadlines?postcode=8004").json()
    assert "Keine Rechtsberatung" in body["disclaimer"]
    assert all("Keine Rechtsberatung" in i["disclaimer"] for i in body["items"])


# ------------------------------------------------------------- API contracts


def test_adr023_api_post_zone_returns_created_zone() -> None:
    zone_id = "z-api-create"
    try:
        resp = c.post(
            "/api/v1/watch/zones",
            json={
                "zone_id": zone_id,
                "postcode": "8004",
                "radius_m": 750,
                "channels": ["push", "email"],
                "consent": True,
                "subscription_endpoint": "https://push.example.test/ep-api",
                "email": "resident@example.ch",
            },
        )
        assert resp.status_code == 200
        body = resp.json()
        assert body["zone_id"] == zone_id
        assert body["channels"] == ["push", "email"]
        assert body["consent"] is True
        assert body["radius_m"] == 750
        assert body["center_source"] == "postcode_pilot_center"
        zones = c.get("/api/v1/watch/zones").json()
        assert zone_id in {z["zone_id"] for z in zones["items"]}
    finally:
        from src.main import _watch

        _watch.delete_zone(zone_id)


def test_adr023_api_events_endpoint_contract_and_kind_validation() -> None:
    body = c.get("/api/v1/watch/events?limit=5").json()
    for key in ("count", "items", "status", "source", "trust_state", "fetched_at"):
        assert key in body, f"missing {key}"
    assert isinstance(body["items"], list)
    assert c.get("/api/v1/watch/events?kind=not_a_kind").status_code == 422
    assert c.get("/api/v1/watch/events?limit=0").status_code == 422


def test_adr023_api_run_endpoint_contract() -> None:
    resp = c.post("/api/v1/watch/run", json={})
    assert resp.status_code == 200
    body = resp.json()
    for key in ("status", "zones_processed", "skipped_no_consent", "events_created",
                "deduplicated", "items", "source", "trust_state", "fetched_at",
                "disclaimer"):
        assert key in body, f"missing {key}"
    assert body["trust_state"] in {"official_publication", "source_pending"}
    assert body["status"] in {"success", "no_zones", "skipped_no_consent",
                             "source_pending"}


def test_adr023_api_zone_requires_consent_and_radius_bounds() -> None:
    payload = {
        "zone_id": "z-api-invalid",
        "lat": ZRH_LAT,
        "lon": ZRH_LON,
        "radius_m": 10,
        "channels": ["push"],
        "consent": True,
        "subscription_endpoint": "https://push.example.test/ep-b",
    }
    assert c.post("/api/v1/watch/zones", json=payload).status_code == 422
    payload["radius_m"] = 500
    payload["channels"] = []
    assert c.post("/api/v1/watch/zones", json=payload).status_code == 422
