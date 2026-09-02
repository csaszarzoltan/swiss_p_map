"""Resident-first information architecture tests."""

from src.services.local_information_service import LocalInformationService


def test_local_briefing_separates_six_resident_topics() -> None:
    result = LocalInformationService().briefing("8004")
    assert len(result.items) == 6
    assert {item.category for item in result.items} == {
        "democracy",
        "environment",
        "weather",
        "housing",
        "mobility",
        "planning",
    }
    assert all(item.source and item.source_url for item in result.items)


def test_pending_live_source_is_not_presented_as_current_news() -> None:
    weather = next(
        x
        for x in LocalInformationService().briefing("8004").items
        if x.category == "weather"
    )
    assert weather.status == "source_pending"
