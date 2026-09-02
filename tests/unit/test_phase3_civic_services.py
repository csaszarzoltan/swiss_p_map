from src.services.connectors.amtsblatt_news_pipeline import AmtsblattNewsPipeline
from src.services.connectors.bfs_voteinfo_client import BfsVoteInfoClient
from src.services.connectors.meteoswiss_client import MeteoSwissClient
from src.services.connectors.sbb_transport_client import SbbTransportClient
from src.services.newsletter_service import NewsletterService, SubscribeRequest
from src.services.web_push_service import PushSubscription, WatchAlert, WebPushService


def test_spec_055_req_055_001_ac_055_001_meteo_cache_metadata():
    assert MeteoSwissClient().current("ZUE").cache_ttl_seconds == 300


def test_spec_056_req_056_001_ac_056_001_voteinfo_hash():
    assert len(BfsVoteInfoClient().sync().sha256) == 64


def test_spec_057_req_057_001_ac_057_001_departures():
    assert SbbTransportClient().departures("Zürich HB")[0].category == "IC"


def test_spec_058_req_058_001_ac_058_001_amtsblatt_ingest():
    assert AmtsblattNewsPipeline().ingest().ingested == 1


def test_spec_059_req_059_001_ac_059_001_newsletter_subscription_double_optin():
    s = NewsletterService()
    x = s.subscribe(
        SubscribeRequest(email="a@example.ch", postcode="8004", consent=True)
    )
    assert s.confirm(str(x["confirmation_token"]))["status"] == "subscribed"


def test_spec_060_req_060_006_ac_060_003_push_deduplication():
    s = WebPushService()
    sub = PushSubscription(endpoint="https://push.example/1", p256dh="x", auth="y")
    s.subscribe(sub)
    a = WatchAlert(
        subscription_endpoint=sub.endpoint, zone_id="z", event_id="e", title="New"
    )
    assert s.alert(a)["status"] == "queued" and s.alert(a)["status"] == "deduplicated"
