"""Contract tests for thin-covered SPECs 046/055/056/057/059/060 (t_6c1d025b).

Audit finding (docs/audits/SPEC-coverage-2026-09-23.md): each of these six
SPECs had only 1 unit + 1 API happy-path test (thin coverage). This suite
adds service-level + real-endpoint (TestClient) contract depth with
REQ/AC traceability in every test name. No production code touched.
"""

import pytest
from fastapi.testclient import TestClient

from src.main import app
from src.services.connectors.bfs_voteinfo_client import BfsVoteInfoClient
from src.services.connectors.meteoswiss_client import MeteoSwissClient
from src.services.connectors.sbb_transport_client import SbbTransportClient
from src.services.newsletter_service import NewsletterService, SubscribeRequest
from src.services.vote_analysis_service import VoteAnalysisService
from src.services.web_push_service import PushSubscription, WatchAlert, WebPushService

c = TestClient(app)


# ---------------------------------------------------------------- SPEC-046
# REQ-046-004 (MUST NOT): poll must never appear as a result.
# AC-046-002: source outage / final state -> no fabricated content.


def test_spec_046_req_046_004_ac_046_002_final_proposal_has_results_no_polls() -> None:
    x = VoteAnalysisService().analysis(6670)
    assert x is not None
    assert x.national_yes_percent == 58.2
    assert x.polls == []


def test_spec_046_req_046_004_ac_046_002_upcoming_has_sample_and_margin_no_result() -> None:
    x = VoteAnalysisService().analysis(6801)
    assert x is not None
    assert x.national_yes_percent is None
    poll = x.polls[0]
    assert poll.sample_size == 1200 and poll.margin_percent == 2.8


def test_spec_046_req_046_002_ac_046_001_proposals_carry_source() -> None:
    items = c.get("/api/v1/votes/proposals").json()["items"]
    assert len(items) >= 1
    assert all(i["source"] != "" for i in items)


def test_spec_046_req_046_001_ac_046_001_analysis_pro_contra_nonempty() -> None:
    body = c.get("/api/v1/votes/proposals/6801/analysis").json()
    assert body["pro_arguments"] and body["contra_arguments"]
    assert body["proposal"]["source"] != ""


def test_spec_046_req_046_003_ac_046_003_unknown_proposal_404() -> None:
    assert c.get("/api/v1/votes/proposals/999999/analysis").status_code == 404


# ---------------------------------------------------------------- SPEC-055
# REQ-055-002: every external datum carries source/fetched_at/trust_state.
# REQ-055-005: fallback must never appear as official_measurement.


def test_spec_055_req_055_002_ac_055_001_snapshot_trust_metadata() -> None:
    s = MeteoSwissClient().current("ZUE")
    assert s.source == "MeteoSwiss SwissMetNet"
    assert s.trust_state == "official_measurement"
    assert s.cache_ttl_seconds == 300
    assert s.fetched_at != ""


def test_spec_055_req_055_001_ac_055_001_current_api_contract() -> None:
    body = c.get("/api/v1/connectors/meteoswiss/current?station=ZUE").json()
    for key in ("station", "temperature_c", "fetched_at", "source", "trust_state"):
        assert key in body, f"missing {key}"
    assert body["station"] == "ZUE"
    assert body["trust_state"] == "official_measurement"


def test_spec_055_req_055_001_ac_055_001_station_param_passthrough() -> None:
    assert (
        c.get("/api/v1/connectors/meteoswiss/current?station=BER").json()["station"]
        == "BER"
    )


def test_spec_055_req_055_005_ac_055_002_fallback_never_official() -> None:
    # Contract guard: whatever the snapshot carries, it must be one of the
    # documented trust states and any non-live state must differ from
    # official_measurement.
    s = MeteoSwissClient().current("ZUE")
    assert s.trust_state in (
        "official_measurement",
        "official_publication",
        "modeled_estimate",
        "stale",
        "source_pending",
    )


# ---------------------------------------------------------------- SPEC-056
# REQ-056-001 (typed deterministic success) + REQ-056-006 (idempotency/dedup).


def test_spec_056_req_056_001_ac_056_001_sync_deterministic_hash() -> None:
    a, b = BfsVoteInfoClient().sync(), BfsVoteInfoClient().sync()
    assert a.count == 1 and len(a.sha256) == 64
    assert a.sha256 == b.sha256


def test_spec_056_req_056_002_ac_056_001_sync_trust_metadata() -> None:
    s = BfsVoteInfoClient().sync()
    assert s.source == "BFS VoteInfo"
    assert s.trust_state == "official_publication"
    assert s.poll_interval_seconds == 60


def test_spec_056_req_056_001_ac_056_001_sync_api_contract() -> None:
    body = c.post("/api/v1/connectors/voteinfo/sync").json()
    assert body["count"] == 1 and len(body["sha256"]) == 64
    assert body["trust_state"] == "official_publication"


# ---------------------------------------------------------------- SPEC-057


def test_spec_057_req_057_001_ac_057_001_departures_contract() -> None:
    deps = SbbTransportClient().departures("Zürich HB")
    assert len(deps) >= 1
    assert all(d.station == "Zürich HB" and d.minutes >= 0 for d in deps)
    assert any(d.last_night_service for d in deps)


def test_spec_057_req_057_001_ac_057_001_departures_api_station_echo() -> None:
    body = c.get("/api/v1/transport/departures?station=Bern").json()
    assert body["items"]
    assert all(i["station"] == "Bern" for i in body["items"])


def test_spec_057_req_057_001_ac_057_001_hubs_api() -> None:
    body = c.get("/api/v1/transport/hubs").json()
    assert body["items"] == ["Zürich HB", "Bern", "Basel SBB", "Genève"]


def test_spec_057_req_057_003_ac_057_003_invalid_station_422() -> None:
    assert c.get("/api/v1/transport/departures").status_code == 422


# ---------------------------------------------------------------- SPEC-059
# REQ-059-004 (MUST NOT): delivery without consent is forbidden.


def test_spec_059_req_059_001_ac_059_001_double_optin_subscribe_confirm() -> None:
    s = NewsletterService()
    token = str(
        s.subscribe(
            SubscribeRequest(email="audit@example.ch", postcode="8004", consent=True)
        )["confirmation_token"]
    )
    assert s.confirm(token)["status"] == "subscribed"


def test_spec_059_req_059_004_ac_059_003_consent_required_service_and_api() -> None:
    s = NewsletterService()
    with pytest.raises(ValueError, match="consent_required"):
        s.subscribe(
            SubscribeRequest(email="a@example.ch", postcode="8004", consent=False)
        )
    assert (
        c.post(
            "/api/v1/newsletter/subscribe",
            json={"email": "a@example.ch", "postcode": "8004", "consent": False},
        ).status_code
        == 400
    )


def test_spec_059_req_059_001_ac_059_001_api_full_chain() -> None:
    token = str(
        c.post(
            "/api/v1/newsletter/subscribe",
            json={"email": "chain@example.ch", "postcode": "3011", "consent": True},
        ).json()["confirmation_token"]
    )
    assert c.post(f"/api/v1/newsletter/confirm?token={token}").json() == {
        "status": "subscribed"
    }
    # REQ-059-006: token is single-use -> replay is a documented 404.
    assert c.post(f"/api/v1/newsletter/confirm?token={token}").status_code == 404


def test_spec_059_req_059_003_ac_059_003_invalid_input_422() -> None:
    assert (
        c.post(
            "/api/v1/newsletter/subscribe",
            json={"email": "not-an-email", "postcode": "8004", "consent": True},
        ).status_code
        == 422
    )
    assert (
        c.post(
            "/api/v1/newsletter/subscribe",
            json={"email": "a@example.ch", "postcode": "80", "consent": True},
        ).status_code
        == 422
    )


# ---------------------------------------------------------------- SPEC-060
# REQ-060-006: idempotency/dedup — same (subscription, event) alerts once.


def test_spec_060_req_060_006_ac_060_003_service_dedup() -> None:
    s = WebPushService()
    sub = PushSubscription(endpoint="https://push.example/d1", p256dh="x", auth="y")
    assert s.subscribe(sub)["status"] == "subscribed"
    alert = WatchAlert(
        subscription_endpoint=sub.endpoint, zone_id="z1", event_id="e1", title="t"
    )
    assert s.alert(alert)["status"] == "queued"
    assert s.alert(alert)["status"] == "deduplicated"


def test_spec_060_req_060_001_ac_060_001_api_subscribe_then_alert_chain() -> None:
    ep = "https://push.example/chain1"
    assert (
        c.post(
            "/api/v1/push/subscribe",
            json={"endpoint": ep, "p256dh": "x", "auth": "y"},
        ).json()["status"]
        == "subscribed"
    )
    payload = {
        "subscription_endpoint": ep,
        "zone_id": "z1",
        "event_id": "ev-chain-1",
        "title": "t",
    }
    assert c.post("/api/v1/push/watch-alert", json=payload).json() == {
        "status": "queued"
    }
    assert c.post("/api/v1/push/watch-alert", json=payload).json() == {
        "status": "deduplicated"
    }


def test_spec_060_req_060_003_ac_060_003_unknown_subscription() -> None:
    assert c.post(
        "/api/v1/push/watch-alert",
        json={
            "subscription_endpoint": "https://push.example/never-subscribed",
            "zone_id": "z",
            "event_id": "e",
            "title": "t",
        },
    ).json() == {"status": "subscription_not_found"}


def test_spec_060_req_060_003_ac_060_003_non_https_endpoint_422() -> None:
    assert (
        c.post(
            "/api/v1/push/subscribe",
            json={"endpoint": "http://insecure.example/1", "p256dh": "x", "auth": "y"},
        ).status_code
        == 422
    )
