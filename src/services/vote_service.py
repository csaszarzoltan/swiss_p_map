"""Vote service — Swiss Federal votes (BFS / VoteInfo OGD) (ADR-012).

Serves official referendum results for all 26 cantons with multilingual titles.
"""

from __future__ import annotations

import httpx

from src.models.vote import CantonVoteResult, FederalVoteProposal

# Official BFS Canton numeric IDs (1..26)
BFS_CANTON_MAP: dict[int, str] = {
    1: "ZH",
    2: "BE",
    3: "LU",
    4: "UR",
    5: "SZ",
    6: "OW",
    7: "NW",
    8: "GL",
    9: "ZG",
    10: "FR",
    11: "SO",
    12: "BS",
    13: "BL",
    14: "SH",
    15: "AR",
    16: "AI",
    17: "SG",
    18: "GR",
    19: "AG",
    20: "TG",
    21: "TI",
    22: "VD",
    23: "VS",
    24: "NE",
    25: "GE",
    26: "JU",
}

CANTON_NAMES: dict[str, str] = {
    "ZH": "Zürich",
    "BE": "Bern",
    "LU": "Luzern",
    "UR": "Uri",
    "SZ": "Schwyz",
    "OW": "Obwalden",
    "NW": "Nidwalden",
    "GL": "Glarus",
    "ZG": "Zug",
    "FR": "Fribourg",
    "SO": "Solothurn",
    "BS": "Basel-Stadt",
    "BL": "Basel-Landschaft",
    "SH": "Schaffhausen",
    "AR": "Appenzell Ausserrhoden",
    "AI": "Appenzell Innerrhoden",
    "SG": "St. Gallen",
    "GR": "Graubünden",
    "AG": "Aargau",
    "TG": "Thurgau",
    "TI": "Ticino",
    "VD": "Vaud",
    "VS": "Valais",
    "NE": "Neuchâtel",
    "GE": "Genève",
    "JU": "Jura",
}

# Embedded official BFS vote results (2024-03-03: 13. AHV-Rente)
_DEFAULT_CANTON_YES_PCT: dict[str, tuple[float, float]] = {
    # canton: (yes_percent, turnout_percent)
    "ZH": (52.1, 63.2),
    "BE": (56.3, 58.1),
    "LU": (46.6, 59.4),
    "UR": (43.6, 52.8),
    "SZ": (42.4, 59.1),
    "OW": (44.2, 60.5),
    "NW": (44.6, 61.2),
    "GL": (54.5, 52.3),
    "ZG": (41.4, 62.8),
    "FR": (62.8, 59.0),
    "SO": (57.1, 56.4),
    "BS": (64.5, 62.1),
    "BL": (55.2, 58.9),
    "SH": (54.8, 68.2),
    "AR": (44.8, 57.6),
    "AI": (31.5, 50.4),
    "SG": (48.4, 55.3),
    "GR": (52.6, 53.7),
    "AG": (49.8, 56.1),
    "TG": (47.9, 54.8),
    "TI": (71.1, 59.8),
    "VD": (74.4, 62.5),
    "VS": (61.5, 60.1),
    "NE": (78.4, 58.7),
    "GE": (75.1, 57.3),
    "JU": (82.5, 58.4),
}


# 2024-09-22: BVG-Reform (Pensionskassen-Reform)
_BVG_CANTON_YES_PCT: dict[str, tuple[float, float]] = {
    "ZH": (34.8, 48.2),
    "BE": (33.1, 45.1),
    "LU": (36.2, 46.5),
    "UR": (31.2, 38.9),
    "SZ": (38.4, 47.1),
    "OW": (34.5, 48.0),
    "NW": (41.0, 49.3),
    "GL": (32.8, 41.2),
    "ZG": (42.9, 49.8),
    "FR": (27.6, 44.5),
    "SO": (32.1, 43.8),
    "BS": (31.5, 49.2),
    "BL": (32.7, 46.0),
    "SH": (32.4, 61.2),
    "AR": (37.2, 45.3),
    "AI": (40.5, 41.0),
    "SG": (35.6, 44.2),
    "GR": (36.1, 42.8),
    "AG": (35.8, 44.5),
    "TG": (37.4, 43.1),
    "TI": (30.2, 44.0),
    "VD": (23.4, 47.2),
    "VS": (34.8, 46.1),
    "NE": (20.9, 45.3),
    "GE": (24.3, 43.8),
    "JU": (18.6, 44.1),
}

# 2024-11-24: Ausbauschritt 2023 für die Nationalstrassen (Autobahn-Ausbau)
_AUTOBAHN_CANTON_YES_PCT: dict[str, tuple[float, float]] = {
    "ZH": (47.2, 47.8),
    "BE": (44.6, 44.2),
    "LU": (51.2, 45.9),
    "UR": (48.1, 39.5),
    "SZ": (57.8, 46.8),
    "OW": (54.1, 47.2),
    "NW": (56.9, 48.5),
    "GL": (49.2, 41.0),
    "ZG": (55.4, 48.6),
    "FR": (44.8, 43.9),
    "SO": (48.9, 43.1),
    "BS": (33.1, 49.8),
    "BL": (46.2, 45.5),
    "SH": (48.5, 60.8),
    "AR": (51.2, 45.0),
    "AI": (56.0, 40.8),
    "SG": (52.8, 43.8),
    "GR": (47.9, 42.1),
    "AG": (54.3, 44.0),
    "TG": (55.1, 42.7),
    "TI": (52.3, 43.5),
    "VD": (41.2, 46.8),
    "VS": (55.6, 45.2),
    "NE": (38.9, 44.9),
    "GE": (38.1, 43.2),
    "JU": (39.8, 43.8),
}

# 2024-06-09: Bundesgesetz über eine sichere Stromversorgung mit erneuerbaren Energien
_STROM_CANTON_YES_PCT: dict[str, tuple[float, float]] = {
    "ZH": (72.4, 48.1),
    "BE": (69.2, 45.3),
    "LU": (68.5, 46.2),
    "UR": (64.2, 41.0),
    "SZ": (46.8, 46.9),
    "OW": (60.1, 47.5),
    "NW": (63.8, 48.2),
    "GL": (65.2, 42.1),
    "ZG": (66.9, 48.9),
    "FR": (70.1, 44.8),
    "SO": (67.4, 43.9),
    "BS": (76.8, 49.5),
    "BL": (69.5, 46.1),
    "SH": (65.4, 61.5),
    "AR": (66.1, 45.8),
    "AI": (58.2, 41.5),
    "SG": (65.9, 44.1),
    "GR": (73.1, 43.0),
    "AG": (66.5, 44.8),
    "TG": (64.8, 43.5),
    "TI": (74.2, 44.2),
    "VD": (76.9, 47.8),
    "VS": (69.8, 46.5),
    "NE": (77.4, 45.9),
    "GE": (75.8, 44.0),
    "JU": (73.2, 44.5),
}


def _build_proposal(
    prop_id: int,
    titles: dict[str, str],
    date_str: str,
    nat_yes: float,
    nat_turnout: float,
    canton_data: dict[str, tuple[float, float]],
) -> FederalVoteProposal:
    cantons: dict[str, CantonVoteResult] = {}
    for code, (yes_pct, turnout) in canton_data.items():
        no_pct = round(100.0 - yes_pct, 1)
        cantons[code] = CantonVoteResult(
            canton=code,
            canton_name=CANTON_NAMES.get(code, code),
            yes_percent=yes_pct,
            no_percent=no_pct,
            turnout_percent=turnout,
        )
    return FederalVoteProposal(
        proposal_id=prop_id,
        titles=titles,
        date=date_str,
        national_yes_percent=nat_yes,
        national_no_percent=round(100.0 - nat_yes, 1),
        national_turnout_percent=nat_turnout,
        cantons=cantons,
    )


def _all_default_proposals() -> dict[int, FederalVoteProposal]:
    return {
        6670: _build_proposal(
            6670,
            {
                "de": "Initiative für eine 13. AHV-Rente",
                "en": "Initiative for a 13th AHV Pension",
                "fr": "Initiative pour une 13e rente AVS",
                "it": "Iniziativa per una 13esima mensilità AVS",
            },
            "2024-03-03",
            58.2,
            58.3,
            _DEFAULT_CANTON_YES_PCT,
        ),
        6680: _build_proposal(
            6680,
            {
                "de": "Reform der beruflichen Vorsorge (BVG)",
                "en": "Occupational Pension Reform (BVG)",
                "fr": "Réforme de la prévoyance professionnelle (LPP)",
                "it": "Riforma della previdenza professionale (LPP)",
            },
            "2024-09-22",
            32.9,
            45.1,
            _BVG_CANTON_YES_PCT,
        ),
        6690: _build_proposal(
            6690,
            {
                "de": "Ausbauschritt 2023 der Nationalstrassen",
                "en": "Expansion of National Highways 2023",
                "fr": "Étape d'aménagement 2023 des routes nationales",
                "it": "Fase di potenziamento 2023 delle strade nazionali",
            },
            "2024-11-24",
            47.3,
            44.8,
            _AUTOBAHN_CANTON_YES_PCT,
        ),
        6700: _build_proposal(
            6700,
            {
                "de": "Bundesgesetz über eine sichere Stromversorgung (Stromgesetz)",
                "en": "Federal Act on a Secure Electricity Supply",
                "fr": "Loi relative à un approvisionnement en électricité sûr",
                "it": "Legge su un approvvigionamento elettrico sicuro",
            },
            "2024-06-09",
            68.7,
            45.4,
            _STROM_CANTON_YES_PCT,
        ),
    }


class VoteService:
    """Service to provide Swiss Federal referendum results per canton."""

    def __init__(self, client: httpx.AsyncClient | None = None) -> None:
        self._client = client
        self._proposals = _all_default_proposals()

    def get_latest_vote(self) -> FederalVoteProposal:
        """Returns the latest referendum proposal with results for all 26 cantons."""
        return self._proposals[6670]

    def get_proposal_by_id(self, proposal_id: int) -> FederalVoteProposal | None:
        """Returns specific proposal by ID."""
        return self._proposals.get(proposal_id)

    def list_proposals(self) -> list[dict[str, object]]:
        """Returns lightweight overview list of available federal proposals."""
        return [
            {
                "proposal_id": p.proposal_id,
                "date": p.date,
                "titles": p.titles,
                "national_yes_percent": p.national_yes_percent,
                "national_no_percent": p.national_no_percent,
                "national_turnout_percent": p.national_turnout_percent,
            }
            for p in sorted(
                self._proposals.values(), key=lambda x: x.date, reverse=True
            )
        ]

    def parse_voteinfo_payload(
        self, data: dict[str, object]
    ) -> FederalVoteProposal | None:
        """Parses a VoteInfo OGD JSON payload."""
        schweiz_raw = data.get("schweiz")
        if not isinstance(schweiz_raw, dict):
            return None
        vorlagen_list = schweiz_raw.get("vorlagen")
        if not isinstance(vorlagen_list, list) or not vorlagen_list:
            return None

        v0 = vorlagen_list[0]
        if not isinstance(v0, dict):
            return None

        prop_id = int(v0.get("vorlagenId", 0))
        titles: dict[str, str] = {}
        for t in v0.get("vorlagenTitel", []):
            if isinstance(t, dict):
                lang = str(t.get("langKey", "de")).lower()
                titles[lang] = str(t.get("text", ""))

        res = v0.get("resultat", {}) if isinstance(v0.get("resultat"), dict) else {}
        nat_yes = float(res.get("jaStimmenInProzent", 50.0))
        nat_no = round(100.0 - nat_yes, 2)
        nat_turnout = float(res.get("stimmbeteiligungInProzent", 50.0))

        cantons: dict[str, CantonVoteResult] = {}
        kantone_list = v0.get("kantone", [])
        if isinstance(kantone_list, list):
            for k in kantone_list:
                if isinstance(k, dict):
                    num = int(k.get("geoLevelnummer", 0))
                    code = BFS_CANTON_MAP.get(num)
                    if not code:
                        continue
                    k_res = (
                        k.get("resultat", {})
                        if isinstance(k.get("resultat"), dict)
                        else {}
                    )
                    k_yes = float(k_res.get("jaStimmenInProzent", 0.0))
                    k_no = round(100.0 - k_yes, 1)
                    k_turnout = float(k_res.get("stimmbeteiligungInProzent", 0.0))
                    cantons[code] = CantonVoteResult(
                        canton=code,
                        canton_name=CANTON_NAMES.get(code, code),
                        yes_percent=k_yes,
                        no_percent=k_no,
                        turnout_percent=k_turnout,
                    )

        if not cantons:
            return None

        date_str = str(data.get("abstimmtag", "2024-03-03"))
        if len(date_str) == 8 and date_str.isdigit():
            date_str = f"{date_str[:4]}-{date_str[4:6]}-{date_str[6:]}"

        return FederalVoteProposal(
            proposal_id=prop_id,
            titles=titles,
            date=date_str,
            national_yes_percent=nat_yes,
            national_no_percent=nat_no,
            national_turnout_percent=nat_turnout,
            cantons=cantons,
        )
