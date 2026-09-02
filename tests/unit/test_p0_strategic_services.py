"""RED/GREEN unit coverage for SPEC-032/034/035/036."""

from src.services.hazard_service import HazardService
from src.services.isos_service import IsosService
from src.services.property_price_service import PropertyPriceService
from src.services.tax_service import TaxService


def test_spec_034_req_001_ac_001_property_segments_and_source() -> None:
    result = PropertyPriceService().get_assessment("ZH", "8004")
    assert result.source == "BFS/FSO IMPI (Immobilienpreisindex)"
    assert {x.segment for x in result.segments} == {
        "single_family_house",
        "condominium",
    }
    assert all(
        x.average_price_chf_m2 > 0 and x.quarterly_index > 0 for x in result.segments
    )


def test_spec_032_req_001_ac_001_tax_all_cantons_ranked() -> None:
    result = TaxService().compare("ZH")
    assert result is not None
    assert len(result.ranking) == 26
    assert result.ranking[0].canton == "ZG"
    assert result.selected.canton == "ZH"
    assert result.neighboring_cantons


def test_spec_032_req_003_ac_005_unknown_canton() -> None:
    assert TaxService().compare("XX") is None


def test_spec_035_req_001_ac_001_bafu_hazard_semantics() -> None:
    result = HazardService().assess("8004", 47.377, 8.52)
    assert result.source.startswith("BAFU/FOEN")
    assert result.risk_level == "medium"
    assert {x.hazard_type for x in result.hazards} >= {"surface_runoff", "flood"}
    assert "absence" in result.disclaimer


def test_spec_036_req_001_ac_001_isos_protection_and_delay_risk() -> None:
    protected = IsosService().assess("8001")
    unprotected = IsosService().assess("8004")
    assert protected.protected is True and protected.classification == "ISOS I"
    assert protected.delay_risk == "high"
    assert unprotected.protected is False and unprotected.classification is None
