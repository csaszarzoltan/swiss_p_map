"""RED/GREEN unit tests for P1/P2 RVAD specifications."""
from src.services.air_quality_service import AirQualityService
from src.services.building_energy_service import BuildingEnergyService
from src.services.connectivity_service import ConnectivityService
from src.services.education_service import EducationService
from src.services.healthcare_service import HealthcareService
from src.services.microclimate_service import MicroclimateService


def test_spec_037_req_001_ac_001_microclimate_scenarios() -> None:
    x=MicroclimateService().assess("8004","ZH"); assert x.source=="MeteoSwiss / CH2025" and len(x.scenarios)==2 and x.scenarios[1].tropical_nights_per_year>x.scenarios[0].tropical_nights_per_year

def test_spec_038_req_001_ac_001_three_education_levels() -> None:
    x=EducationService().facilities("8004"); assert {f.facility_type for f in x.facilities}=={"kindergarten","primary_school","upper_secondary"} and all(f.walking_time_min>0 for f in x.facilities)

def test_spec_043_req_001_ac_001_energy_checklist_and_funding() -> None:
    x=BuildingEnergyService().assess("8004"); assert x.checklist and "dasgebaeudeprogramm" in x.funding_url

def test_spec_040_req_001_ac_001_air_and_pollen_metrics() -> None:
    x=AirQualityService().assess("8004"); assert x.pollutants.pm25_ug_m3>0 and set(x.pollen)=={"hazel","birch","grass"}

def test_spec_041_req_001_ac_001_healthcare_facility_types() -> None:
    x=HealthcareService().access("8004"); assert {f.facility_type for f in x.facilities}=={"pharmacy","urgent_care","hospital"}

def test_spec_042_req_001_ac_001_connectivity_bounds() -> None:
    x=ConnectivityService().status("8004"); assert 0<=x.ftth_percent<=100 and x.average_download_mbps>0
