import pytest
from pydantic import ValidationError

from src.models.geo import AddressSearchResult, CoordinateLV95, CoordinateWGS84
from src.models.place import OeVGueteklasse, PlaceInfo
from src.models.politics import (
    DistrictRepresentatives,
    PoliticalParty,
    Representative,
)


def test_coordinate_wgs84_validation() -> None:
    CoordinateWGS84(latitude=47.3, longitude=8.5)
    with pytest.raises(ValidationError):
        CoordinateWGS84(latitude=100, longitude=8.5)  # lat > 90


def test_coordinate_lv95_validation() -> None:
    CoordinateLV95(easting=2_683_100, northing=1_248_100)
    with pytest.raises(ValidationError):
        CoordinateLV95(easting=1_000_000, northing=1_200_000)


def test_place_info_defaults() -> None:
    p = PlaceInfo(  # type: ignore[call-arg]
        postcode="8004", municipality="Zürich", canton="ZH"
    )
    assert p.oev_class == OeVGueteklasse.NONE
    assert p.steuerfuss_percent is None


def test_representative_serialization() -> None:
    r = Representative(id="1", name="Muster", party=PoliticalParty.SP, wahlkreis="Wahlkreis 4+5")
    assert r.model_dump()["party"] == "SP"
    assert r.proposals == []


def test_district_representatives_structure() -> None:
    d = DistrictRepresentatives(
        district_name="Wahlkreis 4+5",
        postcode="8004",
        canton="ZH",
        representatives=[
            Representative(id="1", name="A", party=PoliticalParty.FDP, wahlkreis="Wahlkreis 4+5"),
        ],
    )
    assert d.postcode == "8004"
    assert len(d.representatives) == 1


def test_address_search_result_roundtrip() -> None:
    a = AddressSearchResult(
        label="8004 Zürich",
        wgs84=CoordinateWGS84(latitude=47.378, longitude=8.54),
        lv95=CoordinateLV95(easting=2683100, northing=1248100),
        canton="ZH",
        municipality="Zürich",
        postcode="8004",
    )
    assert a.model_dump()["postcode"] == "8004"
