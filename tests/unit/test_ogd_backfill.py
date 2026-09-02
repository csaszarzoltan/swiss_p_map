"""OGD 2982 backfill RED→GREEN — mock CSV 8004 (ADR-009)."""

import csv
import io

import httpx
import pytest


def _build_csv(rows: list[dict[str, str]]) -> str:
    header = [
        "id",
        "publicationNumber",
        "publicationDate",
        "entryDeadline",
        "expirationDate",
        "bfs_nr",
        "municipality_name",
        "buildingContractor_legalEntity_selectType",
        "buildingContractor_noUID",
        "buildingContractor_index",
        "buildingContractor_company_legalForm",
        "buildingContractor_company_legalForm_de",
        "buildingContractor_company_address_swissZipCode",
        "buildingContractor_company_address_town",
        "projectFramer_selectType",
        "projectFramer_legalEntity_selectType",
        "projectFramer_noUID",
        "projectFramer_index",
        "projectFramer_company_legalForm",
        "projectFramer_company_legalForm_de",
        "projectFramer_company_address_swissZipCode",
        "projectFramer_company_address_town",
        "delegation_selectType",
        "delegation_buildingContractor_legalEntity_selectType",
        "delegation_buildingContractor_noUID",
        "delegation_buildingContractor_index",
        "delegation_buildingContractor_company_legalForm",
        "delegation_buildingContractor_company_legalForm_de",
        "delegation_buildingContractor_company_address_swissZipCode",
        "delegation_buildingContractor_company_address_town",
        "projectDescription",
        "projectLocation_address_index",
        "projectLocation_address_street",
        "projectLocation_address_houseNumber",
        "projectLocation_address_swissZipCode",
        "projectLocation_address_town",
        "districtCadastre_relation_cadastre",
        "districtCadastre_relation_cadastre_raw",
        "districtCadastre_relation_buildingZone",
        "districtCadastre_relation_district",
        "last_updated",
    ]
    out = io.StringIO()
    w = csv.DictWriter(
        out, fieldnames=header, quoting=csv.QUOTE_MINIMAL, lineterminator="\n"
    )
    w.writeheader()
    for r in rows:
        w.writerow({k: r.get(k, "") for k in header})
    return out.getvalue()


@pytest.mark.asyncio
async def test_ogd_backfill_mock_8004_returns_count_and_upserts() -> None:
    csv_text = _build_csv(
        [
            {
                "id": "ogd-8004-1",
                "publicationNumber": "BP-ZH01-0000099999",
                "publicationDate": "2026-08-20",
                "entryDeadline": "2026-09-09",
                "expirationDate": "2027-08-20",
                "bfs_nr": "261",
                "municipality_name": "Zürich",
                "projectDescription": "Umbau Badenerstrasse 100",
                "projectLocation_address_street": "Badenerstrasse",
                "projectLocation_address_houseNumber": "100",
                "projectLocation_address_swissZipCode": "8004",
                "projectLocation_address_town": "Zürich",
                "districtCadastre_relation_cadastre": "C3519",
                "districtCadastre_relation_buildingZone": "Kernzone",
                "districtCadastre_relation_district": "Zürich",
                "last_updated": "2026-08-20",
            },
            {
                "id": "ogd-8610-1",
                "publicationNumber": "BP-ZH01-0000099998",
                "publicationDate": "2026-08-19",
                "entryDeadline": "2026-09-08",
                "expirationDate": "2027-08-19",
                "bfs_nr": "198",
                "municipality_name": "Uster",
                "projectDescription": "Seefeldstrasse 6 Dachgauben",
                "projectLocation_address_street": "Seefeldstrasse",
                "projectLocation_address_houseNumber": "6",
                "projectLocation_address_swissZipCode": "8610",
                "projectLocation_address_town": "Uster",
                "districtCadastre_relation_cadastre": "C3519",
                "districtCadastre_relation_buildingZone": "K3 - Kernzone",
                "districtCadastre_relation_district": "Uster",
                "last_updated": "2026-08-19",
            },
        ]
    )

    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(
            200, content=csv_text.encode(), headers={"content-type": "text/csv"}
        )

    transport = httpx.MockTransport(handler)
    async with httpx.AsyncClient(transport=transport) as client:
        from src.db.planning_repo import PlanningRepo
        from src.services.ogd_service import OgdService
        from src.services.planning_service import PlanningService

        repo = PlanningRepo(db_path=":memory:")
        ogd = OgdService(client=client)
        svc = PlanningService(repo=repo, ogd=ogd)
        count = await svc.backfill_ogd()
        assert count == 2
        items_8004 = svc.list_items(postcode="8004", active_only=False)
        assert any(i.id == "ogd-8004-1" for i in items_8004)
        items_8610 = svc.list_items(postcode="8610", active_only=False)
        assert any(i.id == "ogd-8610-1" for i in items_8610)


@pytest.mark.asyncio
async def test_ogd_backfill_empty_csv_returns_0() -> None:
    csv_text = _build_csv([])

    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(
            200, content=csv_text.encode(), headers={"content-type": "text/csv"}
        )

    transport = httpx.MockTransport(handler)
    async with httpx.AsyncClient(transport=transport) as client:
        from src.db.planning_repo import PlanningRepo
        from src.services.ogd_service import OgdService
        from src.services.planning_service import PlanningService

        repo = PlanningRepo(db_path=":memory:")
        ogd = OgdService(client=client)
        svc = PlanningService(repo=repo, ogd=ogd)
        count = await svc.backfill_ogd()
        assert count == 0
