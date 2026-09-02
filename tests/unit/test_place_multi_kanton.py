"""Tesztek az országos (multi-kanton) hely- és körzetfeloldáshoz (ADR-011)."""

import httpx
import pytest

from src.models.place import OeVGueteklasse
from src.services.place_service import PlaceService
from src.services.politics_service import PoliticsService


class TestMultiKantonPlace:
    def test_place_stubs_include_quick_picks(self) -> None:
        """A Quick-Pick kantonok (Bern, Basel, Uster, Genf) megtalálhatók a PlaceService-ben."""
        service = PlaceService()
        for pc, expected_muni, expected_canton in [
            ("8004", "Zürich", "ZH"),
            ("8001", "Zürich", "ZH"),
            ("8610", "Uster", "ZH"),
            ("3011", "Bern", "BE"),
            ("4001", "Basel", "BS"),
            ("1201", "Genève", "GE"),
        ]:
            info = service.get_by_postcode(pc)
            assert info is not None, f"Hiányzó postcode: {pc}"
            assert info.municipality == expected_muni
            assert info.canton == expected_canton

    @pytest.mark.asyncio
    async def test_place_live_bern_skips_zh_scrapers(self) -> None:
        """Bern (3011) esetén a szövetségi rétegek lefutnak, a ZH-specifikus kapuk nem aktiválódnak."""

        def handler(request: httpx.Request) -> httpx.Response:
            url_str = str(request.url)
            if "ch.are.gueteklassen_oev" in url_str:
                return httpx.Response(
                    200,
                    json={
                        "results": [
                            {
                                "layerBodId": "ch.are.gueteklassen_oev",
                                "attributes": {
                                    "klasse_de": "A - sehr gute Erschliessung"
                                },
                            }
                        ]
                    },
                )
            if "ch.bfe.solarenergie-eignung-daecher" in url_str:
                return httpx.Response(
                    200,
                    json={
                        "results": [
                            {
                                "layerBodId": "ch.bfe.solarenergie-eignung-daecher",
                                "attributes": {"mstrahlung": 1150.0, "klasse": 3},
                            }
                        ]
                    },
                )
            if "ch.bafu.larm-strassenlaerm_tag" in url_str:
                return httpx.Response(200, json={"results": []})
            # ZH WFS vagy Steueramt nem szabad, hogy meghívódjon vagy hibát okozzon
            return httpx.Response(404, text="Not Found")

        client = httpx.AsyncClient(transport=httpx.MockTransport(handler))
        service = PlaceService(client=client)
        info = await service.get_by_postcode_live("3011")

        assert info is not None
        assert info.postcode == "3011"
        assert info.canton == "BE"
        assert info.oev_class == OeVGueteklasse.A
        assert info.solar_kwh_m2 == 1150.0
        assert info.solar_class == "gut"
        assert info.oereb_zone is None  # ZH WFS kihagyva


class TestMultiKantonPolitics:
    def test_politics_stubs_include_quick_picks(self) -> None:
        """A Quick-Pick városokhoz elérhető politikai képviselet."""
        service = PoliticsService()
        for pc, expected_district, expected_canton in [
            ("8004", "Wahlkreis 4+5", "ZH"),
            ("8610", "Gemeinderat Uster", "ZH"),
            ("3011", "Stadtrat Bern", "BE"),
            ("4001", "Grosser Rat Basel-Stadt", "BS"),
        ]:
            data = service.get_by_postcode(pc)
            assert data is not None, f"Hiányzó politics postcode: {pc}"
            assert data.canton == expected_canton
            assert len(data.representatives) > 0
