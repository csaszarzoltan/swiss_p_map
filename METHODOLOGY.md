# Módszertani Elvárások — Swiss P Map

## 1. Kódolási szabályok
### Fájlstruktúra
- Új modul: `src/<modul>.py` vagy `src/services/<feature>.py`, `src/models/<domain>.py`
- Új unit teszt: `tests/unit/test_<modul>.py`
- API/E2E teszt: `tests/e2e/test_<feature>_e2e.py` vagy `tests/test_<feature>.py`
- Frontend: `frontend/` (Next.js + MapLibre) — `app/`, `components/`, `lib/`
- Docs: `docs/research/YYYY-MM-DD-*.md`, `docs/decisions/ADR-*.md`, `docs/competitor/YYYY-Www-scan.md`

### Kódolási stílus
- Python 3.11+ (type hints kötelező, `from __future__ import annotations`)
- f-string használata
- Docstring minden publikus osztályon és metóduson
- Maximum 400 sor fájlonként; 200 felett bonts kisebb modulokra
- Konstansok fájl tetején
- Import sorrend: stdlib → third-party → local
- Frontend: `escapeHtml` minden felhasználói szövegnél

### Osztálytervezés
- Dependency injection (paraméterben kapja meg a függőségeket)
- Frozen dataclass / Pydantic BaseModel ahol értelmes
- Enum használata értéknaplózáshoz
- Protocol interfészek határozzák meg a szerződéseket

## 2. API endpoint szabályok

### Válasz formátum
```json
// Sikeres
{"status": "ok", "data": {...}}
// Lista
{"items": [...]}
// Hiba
{"error": "error_type"}
```

### HTTP státuszkódok
- 200: Sikeres művelet
- 201: Létrehozás
- 400: Hibás kérés (validálási hiba)
- 404: Nem található
- 409: Ütközés (pl. idempotencia)
- 500: Szerver hiba

### Security
- Bemeneti validálás minden POST endpointon (Pydantic / `field_validator`)
- XSS prevention (escapeHtml JavaScriptben)
- Security headers (X-Content-Type-Options, X-Frame-Options, CSP)

## 3. Tesztelési szabályok

### Teszt lefedettség
- Minden publikus metódusra legyen teszt
- Happy path + edge case + error case
- Mockoljuk a külső szolgáltatásokat (Swisstopo API, PARIS-API, LLM gateway)
- Integrációs teszt a teljes láncra ahol értelmes (pl. `geo convert → API`)

### Teszt elnevezés
```python
class TestFeatureName:
    def test_happy_path_scenario(self):
        """Leírás mit tesztel."""
        pass

    def test_error_handling_when_X(self):
        """Hibakezelés tesztelése."""
        pass
```

### Teszt futtatás
```bash
# Összes teszt (pytest) — ez a valódi futtatás
PATH=.venv/bin:$PATH pytest -q
# Unit csak
PATH=.venv/bin:$PATH pytest tests/unit -q 2>/dev/null || PATH=.venv/bin:$PATH pytest tests -q -k "unit"
# E2E (böngésző/HTTP)
PATH=.venv/bin:$PATH pytest tests/e2e -q
# Szintaxis
python -m compileall -q src tests
# Típusellenőrzés
PATH=.venv/bin:$PATH mypy src tests --ignore-missing-imports
```

## 4. Git szabályok

### Commit formátum
```
<scope>: <rövid leírás>

- Részletes leírás
- Miért kellett a változás
```

Példák:
- `feat: LV95 ↔ WGS84 konverter`
- `fix: Swisstopo geocoder hibakezelés`
- `test: Unit tesztek a geo_converter-hez`
- `docs: ADR-002 adatpipeline`
- `chore: CI mypy beépítése`

### Branch kezelés
- `master`: Stabil, production-ready (közvetlen commit + push a kis scope-ú fixeknél)
- `feature/<név>`: Nagyobb funkciók (opcionális)
- Minden commit előtt: `git diff --stat`, `python -m compileall -q`, releváns tesztek zöldek
- Push után: `git status --short` tiszta

## 5. Dokumentáció szabályok — döntések és kutatás (kötelező)

### ADR és research kötelezés
- `researcher` nem zárhat kártyát ADR nélkül: minden nagyobb döntés → 1 `docs/decisions/ADR-NNN-{slug}.md` (max 1 oldal, template: `ADR-000-template.md`). `proposed → accepted` státusz, `docs/research/YYYY-MM-DD-*.md` linkkel.
- `researcher` nyers anyag: `docs/research/YYYY-MM-DD-{tema}.md` (max 5 oldal, **comparison table kötelező** ha több opció). Kanban comment csak linket tesz.
- Heti scout (cron): `docs/competitor/YYYY-Www-scan.md` (triage, BLOCKED emberi jóváhagyásig — ember nélkül nem indul dev).
- Evidence TTL: képernyőképek / időszakos riportok (pl. screenshots, futtatási bizonyítékok) 30 nap után törlődnek; docs/archive 90 nap után tömörítve. Monolit doc nem nőhet: `docs/API.md` új endpointja már `docs/api/<feature>.md`-be kerül.

### README.md
- Projekt leírás
- Telepítés
- Használat
- API referencia (link)

### CHANGELOG.md
- Új funkciók
- Hibajavítások
- Megszakító változások

### CODE docstring
- Osztály: Mi a felelőssége
- Metódus: Mit csinál, paraméterek, visszatérési érték
- Példa használat (ha nem egyértelmű)

## 6. Minőségi kapuk (Kötelező)

### Commit előtt
1. `python -m compileall -q src tests` → Szintaktikai hiba nélkül
2. Releváns tesztek zöldek: `PATH=.venv/bin:$PATH pytest -q` (vagy legalább `tests/unit`)
3. `PATH=.venv/bin:$PATH mypy src tests --ignore-missing-imports` ha Python változott (strict a pyproject.toml szerint)
4. `git diff --stat` → Ellenőrzés

### Push előtt
1. `git pull --rebase` → Merge conflict nélkül (opcionális kis repo-nál)
2. `git push` → Sikeres
3. `git status --short` → Tiszta

### Átadás előtt
1. Teszt szám pontosság
2. Fájlnevek egyeznek a tervekkel
3. Nincs nem tervezett módosítás

## 7. Swiss P Map specifikus

- Koordinátarendszer: LV95 / EPSG:2056 ↔ WGS84 / EPSG:4326 (PyProj + Swisstopo approximációs képlet tesztekhez)
- OGD források: Swisstopo, Zürich OGD, PARIS-API, Amtsblattportal — mind mockolva tesztekben
- LLM gateway (ha lesz): lokális proxy `http://127.0.0.1:8000/v1`, 120s timeout
- MVP fókusz: Kanton + Stadt Zürich (ADR-001)

## 8. Evolúciós rendszer (kötelező)
- **Master:** `docs/methodology/EVOLUTIONARY-SYSTEM.md` — behavior-first, 7 fázis, US+gui_flow → RED → prototípus stop-gate → GREEN → continuous E2E (4 réteg)
- **Függelék:** `docs/methodology/BROWSER-HELPER-MCP.md` — Browser Helper valós API (`/agent/observe`, `/agent/act`, `/page/analyze`, `/headless/screenshot`), tenant izoláció, record→replay
- **Gate-ek:** US min 4 story (happy/edge/error/gui), BDD-gate fájlnév-alapú, ledger `verify --evidence`, canary hermes cron `no_agent`
