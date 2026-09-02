"""Unit TDD coverage for final roadmap SPEC/REQ/AC chains."""

from src.services.cadastral_service import CadastralService
from src.services.district_comparison_service import DistrictComparisonService
from src.services.objection_workspace_service import (
    ObjectionRequest,
    ObjectionWorkspaceService,
)
from src.services.provenance_service import ProvenanceService
from src.services.transit_mobility_service import TransitMobilityService


def test_spec_028_req_001_ac_001_comparison_matrix() -> None:
    rows = DistrictComparisonService().compare(["8004", "3011", "6300"])
    assert len(rows) == 3 and all(r.price_chf_m2 > 0 for r in rows)


def test_spec_033_req_001_ac_001_sbb_isochrones() -> None:
    x = TransitMobilityService().assess("8004")
    assert x.source == "SBB / OpenData.ch" and {h.zone for h in x.hubs} <= {
        15,
        30,
        45,
        60,
    }


def test_spec_026_req_001_ac_001_cadastral_parcel() -> None:
    x = CadastralService().parcel("8004", "5120")
    assert x.area_m2 > 0 and x.trust_state == "cadastral_registry"


def test_spec_039_req_001_ac_001_objection_disclaimer() -> None:
    x = ObjectionWorkspaceService().create(
        ObjectionRequest(
            baugesuch_id="demo-1",
            reason_category="noise",
            user_notes="Bitte Lärm prüfen",
        )
    )
    assert "Keine Rechtsberatung" in x.disclaimer and x.checklist


def test_spec_029_req_001_ac_001_provenance_states() -> None:
    rows = ProvenanceService().list_sources()
    assert {x.trust_state for x in rows} >= {
        "official_measurement",
        "modeled_estimate",
        "cadastral_registry",
    }
