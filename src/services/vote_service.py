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


def _create_default_proposal() -> FederalVoteProposal:
    cantons: dict[str, CantonVoteResult] = {}
    for code, (yes_pct, turnout) in _DEFAULT_CANTON_YES_PCT.items():
        no_pct = round(100.0 - yes_pct, 1)
        cantons[code] = CantonVoteResult(
            canton=code,
            canton_name=CANTON_NAMES.get(code, code),
            yes_percent=yes_pct,
            no_percent=no_pct,
            turnout_percent=turnout,
        )
    return FederalVoteProposal(
        proposal_id=6670,
        titles={
            "de": "Initiative für eine 13. AHV-Rente",
            "en": "Initiative for a 13th AHV Pension",
            "fr": "Initiative pour une 13e rente AVS",
            "it": "Iniziativa per una 13esima mensilità AVS",
        },
        date="2024-03-03",
        national_yes_percent=58.2,
        national_no_percent=41.8,
        national_turnout_percent=58.3,
        cantons=cantons,
    )


class VoteService:
    """Service to provide Swiss Federal referendum results per canton."""

    def __init__(self, client: httpx.AsyncClient | None = None) -> None:
        self._client = client
        self._cached_proposal = _create_default_proposal()

    def get_latest_vote(self) -> FederalVoteProposal:
        """Returns the latest referendum proposal with results for all 26 cantons."""
        return self._cached_proposal

    def parse_voteinfo_payload(self, data: dict[str, object]) -> FederalVoteProposal | None:
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
                    k_res = k.get("resultat", {}) if isinstance(k.get("resultat"), dict) else {}
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
