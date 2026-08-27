from src.models.place import PlaceInfo
def test_risk_fields_are_backward_compatible():
 p=PlaceInfo(postcode="8004",municipality="Zurich",canton="ZH",steuerfuss_percent=119,noise_db_day=55,oev_class="A",gwr_building_count=1,solar_kwh_m2=1,solar_class="good",oereb_zone="Kernzone",steuerfuss_source="test",risk_level="high",risk_reason="Core zone")
 assert p.risk_level=="high" and p.risk_reason=="Core zone"
