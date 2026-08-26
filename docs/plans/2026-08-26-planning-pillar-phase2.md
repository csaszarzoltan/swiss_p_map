# Planning Pillár (Phase 2) — Research & Implementation Plan

> **For Hermes:** Use subagent-driven-development skill to implement this plan task-by-task.
> **ELŐFELTÉTEL:** A Task 0 (research) eredménye ADR-002-be vezet; kód CSAK utána indul (módszertan: research → ADR → dev).

**Goal:** Építési engedélykérelmek (Baugesuche) megjelenítése a térképen a 20 napos Auflage-ablakban, ÖREB zónainformációval.

**Architecture:** Python ETL-szolgáltatás (`src/services/planning_service.py`) az Amtsblattportal API-t hívja (cron vagy on-demand), GeoJSON-vá normalizál, FastAPI-n keresztül szolgálja ki. A 20 napos lejárat után a rekord inaktív (soft TTL).

**Tech Stack:** httpx, Shapely (geometry), meglévő Pydantic modell-réteg.

---

## Task 0: Adatforrás-kutatás → ADR-002 (KÓD ELŐTT)

**Objective:** Bizonyított API-kontraktum az Amtsblattportal + ÖREB M2M felől.

**Files:**
- Create: `docs/research/2026-MM-DD-amtsblatt-oereb-api.md`
- Create: `docs/decisions/ADR-002-data-ingestion-pipeline.md`

**Step 1: API-feltérképezés**

- `https://www.amtsblattportal.ch/docs/api` — publikációs típusok, szűrés kanton/period/typus szerint
- Baugesuch-releváns publikációk mezőlistája (cím, település, koordináta?, PDF-link, Auflage-kezdet/vég)
- ÖREB M2M: kantononkénti végpont (ZH), DATA-extract formátum (XML kötelező / JSON opcionális)

**Step 2: Döntési kérdések az ADR-be**

1. Van-e gépi koordináta a Baugesuch-publikációkban? Ha nincs → geokódolás településnévvel (pontosság-kompromisszum dokumentálva)
2. Polling gyakoriság (napi 1 elég? Az Amtsblatt naponta frissül)
3. Tárolás: memória-cache (MVP) vs PostGIS (később) — MVP: SQLite + TTL oszlop
4. Jogi: csak publikus Auflage-adatok, forrás-link minden rekordon

**Step 3: ADR-002 sablon kitöltése** (proposed státusz, emberi jóváhagyás before code)

**Commit:** `docs: Planning pillér kutatás + ADR-002 (proposed)`

---

### Task 1: Planning domain modellek (ADR-002 accepted UTÁN)

**Files:**
- Create: `src/models/planning.py`
- Test: `tests/unit/test_planning_models.py`

**Step 1: Failing test**

```python
from datetime import date
from src.models.planning import Baugesuch


def test_baugesuch_active_within_aufage() -> None:
    b = Baugesuch(
        id="ab-1", title="Neubau Mehrfamilienhaus",
        municipality="Zürich", postcode="8004",
        auflage_start=date(2026, 8, 20), auflage_end=date(2026, 9, 8),
        source_url="https://amtsblattportal.ch/...",
    )
    assert b.is_active(date(2026, 9, 1)) is True
    assert b.is_active(date(2026, 9, 9)) is False
```

**Step 2:** futtatás → FAIL (modul nem létezik)

**Step 3: Implementáció**

```python
"""Planning models — Baugesuch with Auflage window."""
from __future__ import annotations
from datetime import date
from pydantic import BaseModel, Field


class Baugesuch(BaseModel):
    id: str
    title: str
    municipality: str
    postcode: str
    auflage_start: date
    auflage_end: date
    source_url: str
    lat: float | None = None
    lon: float | None = None

    def is_active(self, on: date) -> bool:
        """True ha az Auflage-ablakban van (Einsprache lehetséges)."""
        return self.auflage_start <= on <= self.auflage_end
```

**Step 4:** PASS → **Step 5:** `git commit -m "feat: Baugesuch modell Auflage-ablak logikával"`

---

### Task 2: Amtsblatt client (mockolt)

**Files:**
- Create: `src/services/amtsblatt_service.py`
- Test: `tests/unit/test_amtsblatt_service.py`

Minta: `swisstopo_service.py` mintájára — Protocol-injektált httpx client, `fetch_publications(canton="ZH", since=...)`, HTTP-hibánál üres lista. Mock-tesztek: 1 találat / 0 találat / hiba / rossz mező skip.

**Commit:** `feat: Amtsblatt client (DI, mocked)`

---

### Task 3: Planning service + endpoint

**Files:**
- Create: `src/services/planning_service.py`
- Modify: `src/main.py`
- Test: `tests/e2e/test_core_e2e.py`

Endpoint: `GET /api/v1/planning/baugesuche?postcode=8004&active_only=true`
Válasz: `{"items": [Baugesuch...]}` (METHODOLOGY lista-formátum)
E2E: aktív stub-rekordtal 200 + items≥1; ismeretlen postcode → 404.

**Commit:** `feat: /api/v1/planning/baugesuche végpont`

---

### Task 4: Frontend réteg

**Files:**
- Modify: `frontend/src/lib/api.ts` (+planning típus)
- Modify: `frontend/src/app/page.tsx` (panel bővítés)
- Modify: `frontend/src/app/Map.tsx` (Baugesuch markerek, eltérő szín)

Build + tsc zöld, commit: `feat: Baugesuche a térképen`

---

### Task 5: ÖREB zóna-lekérdezés (külön kártya, ha Task 0 igazolja az M2M-et)

Kanton ZH végpont + XML parse (Shapely-mentes MVP: csak zónanév visszaadása postcode→parcella helyett községi szinten). Kockázat: M2M komplexitás — külön research igényel, ne ebben a ciklusban.

## Verification

- [ ] ADR-002 accepted emberi jóváhagyással
- [ ] `pytest -q` → összes zöld (unit+E2E)
- [ ] mypy/ruff clean
- [ ] Frontend build zöld
- [ ] Minden rekordban `source_url` (jogi nyomonkövethetőség)
