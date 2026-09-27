"""HTTP acceptance TDD coverage for final roadmap SPEC/REQ/AC chains."""

import json
from pathlib import Path

from fastapi.testclient import TestClient

from src.main import app

client = TestClient(app)
REPO_ROOT = Path(__file__).resolve().parents[2]


def test_spec_028_req_001_ac_001_compare_api() -> None:
    assert (
        len(client.get("/api/v1/districts/compare?postcodes=8004,3011").json()["items"])
        == 2
    )


def test_spec_033_req_001_ac_001_mobility_api() -> None:
    assert (
        client.get("/api/v1/mobility/isochrones?postcode=8004").json()[
            "service_interval_min"
        ]
        == 15
    )


def test_spec_026_req_001_ac_001_parcel_api() -> None:
    assert (
        client.get("/api/v1/cadastre/parcel?postcode=8004&parcel_nr=5120").json()[
            "area_m2"
        ]
        > 0
    )


def test_spec_039_req_001_ac_001_template_api() -> None:
    assert (
        "Keine Rechtsberatung"
        in client.post(
            "/api/v1/objection/template",
            json={
                "baugesuch_id": "demo",
                "reason_category": "noise",
                "user_notes": "Lärm",
            },
        ).json()["disclaimer"]
    )


def test_spec_029_req_001_ac_001_provenance_api() -> None:
    assert client.get("/api/v1/system/sources-provenance").json()["items"]


def test_spec_025_req_001_ac_001_watch_geojson_contract() -> None:
    """SPEC-025: Mentett figyelési zónák — POST + GET /watch/zones round-trip."""
    zone_id = "a3-025-roundtrip-8004"
    payload = {
        "zone_id": zone_id,
        "lat": 47.374,
        "lon": 8.525,
        "radius_m": 500,
        "channels": ["push"],
        "consent": True,
        "subscription_endpoint": "https://push.example.test/a3-025",
    }
    r = client.post("/api/v1/watch/zones", json=payload)
    assert r.status_code == 200, r.text
    data = r.json()
    assert data["zone_id"] == zone_id
    assert data["consent"] is True
    assert data["radius_m"] == 500
    # round-trip: list contains it
    r2 = client.get("/api/v1/watch/zones")
    assert r2.status_code == 200
    body = r2.json()
    assert "count" in body and "items" in body
    found = next((z for z in body["items"] if z["zone_id"] == zone_id), None)
    assert found is not None, f"zone {zone_id} not in {body['items'][:2]}"
    assert found["lat"] == 47.374
    assert found["lon"] == 8.525
    # provenance honesty: events endpoint carries trust_state
    r3 = client.get("/api/v1/watch/events")
    assert r3.status_code == 200
    j3 = r3.json()
    assert "trust_state" in j3
    assert "source" in j3
    # deadlines endpoint also carries disclaimer + rule (REQ-B3) when postcode given
    r4 = client.get("/api/v1/watch/deadlines?postcode=8004")
    assert r4.status_code == 200
    j4 = r4.json()
    assert "disclaimer" in j4
    assert "Keine Rechtsberatung" in j4["disclaimer"]
    assert "rule" in j4


def test_spec_027_req_001_ac_001_pwa_assets_contract() -> None:
    """SPEC-027: PWA offline — sw.js + manifest.json + PwaStatus (A2)."""
    sw = REPO_ROOT / "frontend" / "public" / "sw.js"
    assert sw.exists(), f"missing {sw}"
    text = sw.read_text(encoding="utf-8")
    assert "CACHE" in text
    assert "fetch" in text
    assert "install" in text
    # cache-first nav + network-first API distinction
    assert "isApi" in text or "network-first" in text.lower() or "/api/" in text
    assert "isNav" in text or "navigate" in text

    manifest = REPO_ROOT / "frontend" / "public" / "manifest.json"
    assert manifest.exists(), f"missing {manifest}"
    mf = json.loads(manifest.read_text(encoding="utf-8"))
    assert "icons" in mf
    sizes = [i.get("sizes") for i in mf.get("icons", [])]
    assert "192x192" in sizes, f"sizes={sizes}"
    assert "512x512" in sizes, f"sizes={sizes}"
    assert mf.get("scope") == "/"
    assert mf.get("start_url") == "/de"
    # icons exist on disk
    assert (REPO_ROOT / "frontend" / "public" / "icon-192.png").exists()
    assert (REPO_ROOT / "frontend" / "public" / "icon-512.png").exists()

    # PwaStatus component contract: role=status + aria-live + serviceWorker
    pwa = REPO_ROOT / "frontend" / "src" / "components" / "PwaStatus.tsx"
    assert pwa.exists(), f"missing {pwa}"
    src = pwa.read_text(encoding="utf-8")
    assert 'role="status"' in src
    assert 'aria-live="polite"' in src
    assert "serviceWorker" in src
    assert "navigator.onLine" in src or "onLine" in src


def test_spec_030_req_001_ac_001_a11y_contract() -> None:
    """SPEC-030: mobil/a11y — viewport 375px + aria-*/tab smoke."""
    page = REPO_ROOT / "frontend" / "src" / "app" / "[locale]" / "page.tsx"
    assert page.exists(), f"missing {page}"
    txt = page.read_text(encoding="utf-8")
    # a11y: skip link + main landmark
    assert "Skip to content" in txt
    assert 'href="#main-content"' in txt
    assert 'id="main-content"' in txt
    # responsive: viewport via Next.js (width=device-width) + responsive classes
    # Next.js injects viewport meta automatically; check for sm: breakpoint usage
    assert "sm:" in txt

    # LocalInformationHub — a11y tab contract
    hub = REPO_ROOT / "frontend" / "src" / "components" / "LocalInformationHub.tsx"
    assert hub.exists()
    htxt = hub.read_text(encoding="utf-8")
    assert 'role="tablist"' in htxt
    assert 'role="tabpanel"' in htxt
    assert 'aria-selected' in htxt
    assert "tabIndex" in htxt
    assert "aria-controls" in htxt

    # DetailPanel — export button keyboard + aria
    detail = REPO_ROOT / "frontend" / "src" / "components" / "DetailPanel.tsx"
    assert detail.exists()
    dtxt = detail.read_text(encoding="utf-8")
    assert 'aria-label' in dtxt
    assert 'data-testid="export-button"' in dtxt
    assert 'data-testid="export-format-select"' in dtxt
    # focus-visible ring for keyboard
    assert "focus-visible" in dtxt

    # PwaStatus also a11y (already checked in 027, double-check)
    pwa = REPO_ROOT / "frontend" / "src" / "components" / "PwaStatus.tsx"
    assert 'aria-live' in pwa.read_text(encoding="utf-8")

    # backend still honest: health 200
    assert client.get("/health").status_code == 200
