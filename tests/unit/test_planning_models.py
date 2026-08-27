"""Unit: Baugesuch domain model (Auflage-ablak). RED→GREEN Task 1."""

from datetime import date

import pytest
from pydantic import ValidationError

from src.models.planning import AUFLAGE_DAYS, Baugesuch


def test_baugesuch_active_within_aufage() -> None:
    b = Baugesuch(
        id="ab-1",
        title="Neubau Mehrfamilienhaus",
        municipality="Zürich",
        municipality_id=261,
        postcode="8004",
        canton="ZH",
        publication_date=date(2026, 8, 20),
        expiration_date=date(2027, 8, 20),
        auflage_start=date(2026, 8, 20),
        auflage_end=date(2026, 9, 8),
        source_url="https://amtsblattportal.ch/api/v1/publications/ab-1/xml",
        geocode_precision="locality",
    )
    assert b.is_active(date(2026, 8, 20)) is True  # inclusive start
    assert b.is_active(date(2026, 9, 1)) is True
    assert b.is_active(date(2026, 9, 8)) is True  # inclusive end
    assert b.is_active(date(2026, 9, 9)) is False
    assert b.is_active(date(2026, 8, 19)) is False


def test_baugesuch_default_aufage_end_is_20_days() -> None:
    b = Baugesuch(
        id="ab-2",
        title="Abbruch",
        municipality="Uster",
        postcode="8610",
        canton="ZH",
        publication_date=date(2026, 8, 26),
        expiration_date=date(2027, 8, 26),
        source_url="https://amtsblattportal.ch/api/v1/publications/ab-2/xml",
    )
    assert b.auflage_start == date(2026, 8, 26)
    assert b.auflage_end == date(2026, 9, 15)  # +20
    assert AUFLAGE_DAYS == 20


def test_baugesuch_validation() -> None:
    with pytest.raises(ValidationError):
        Baugesuch(
            id="",
            title="X",
            municipality="Zürich",
            postcode="8004",
            canton="ZH",
            publication_date=date(2026, 8, 20),
            expiration_date=date(2027, 8, 20),
            source_url="https://amtsblattportal.ch/api/v1/publications/x/xml",
        )


def test_baugesuch_inspector_fields_and_risk_scoring() -> None:
    """Inspector mezők és kockázati besorolás ellenőrzése (ADR-016)."""
    # High risk (Aufstockung / Kernzone)
    b_high = Baugesuch(
        id="bg-high",
        title="Badenerstrasse 120, 8004 Zürich — Dachausbau & Aufstockung in Kernzone",
        municipality="Zürich",
        postcode="8004",
        canton="ZH",
        publication_date=date(2026, 8, 20),
        expiration_date=date(2027, 8, 20),
        source_url="https://amtsblattportal.ch/api/v1/publications/bg-high/xml",
        contractor="Immo AG",
        architect="EM2N",
        parcel_number="Kat.-Nr. 4812",
        zone_type="Kernzone (K)",
    )
    assert b_high.risk_level == "high"
    assert b_high.contractor == "Immo AG"
    assert b_high.architect == "EM2N"
    assert b_high.parcel_number == "Kat.-Nr. 4812"

    # Medium risk (Neubau)
    b_med = Baugesuch(
        id="bg-med",
        title="Neubau Gewerbegebäude",
        municipality="Bern",
        postcode="3011",
        canton="BE",
        publication_date=date(2026, 8, 20),
        expiration_date=date(2027, 8, 20),
        source_url="https://amtsblattportal.ch/api/v1/publications/bg-med/xml",
    )
    assert b_med.risk_level == "medium"

    # Low risk (Renovation / default)
    b_low = Baugesuch(
        id="bg-low",
        title="Fassadenanstrich",
        municipality="Basel",
        postcode="4001",
        canton="BS",
        publication_date=date(2026, 8, 20),
        expiration_date=date(2027, 8, 20),
        source_url="https://amtsblattportal.ch/api/v1/publications/bg-low/xml",
    )
    assert b_low.risk_level == "low"
