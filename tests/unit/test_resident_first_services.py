from src.services.cost_of_living_service import CostOfLivingService
from src.services.local_information_service import LocalInformationService
from src.services.local_news_service import LocalNewsService
from src.services.municipal_service import MunicipalService
from src.services.vote_analysis_service import VoteAnalysisService
from src.services.weather_climate_service import WeatherClimateService


def test_spec_045_req_045_001_ac_045_001_briefing():
    assert LocalInformationService().briefing("8004").items


def test_spec_046_req_046_001_ac_046_001_voting_analysis_pro_contra():
    x = VoteAnalysisService().analysis(6801)
    assert x and x.pro_arguments and x.polls[0].sample_size == 1200


def test_spec_047_req_047_004_ac_047_002_news_pending():
    assert LocalNewsService().get_local("8004").status == "source_pending"


def test_spec_048_req_048_001_ac_048_001_weather():
    x = WeatherClimateService()
    assert x.alerts()[0].level in range(1, 6) and x.water()


def test_spec_049_req_049_001_ac_049_001_costs():
    x = CostOfLivingService().assess("8004", 120000)
    assert x.total_monthly_chf > 0


def test_spec_050_req_050_001_ac_050_001_municipal():
    assert MunicipalService().waste("8004").events
