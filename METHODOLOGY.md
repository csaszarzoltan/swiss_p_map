# Módszertani Elvárások — AI Product Engineering Control Plane

## 1. Kódolási szabályok
### Fájlstruktúra
- Új modul: `control_plane/<modul_név>.py` (vagy `control_plane/routes/<feature>_routes.py` API-khoz)
- Új unit teszt: `tests/unit/test_<modul_név>.py`
- API/E2E teszt: `tests/e2e/test_<feature>_e2e.py` vagy `tests/test_<feature>.py`
- Frontend: `control_plane/static/app.js` (view-k szerint szekcionálva), `index.html`, `styles.css`

### Kódolási stílus
- Python 3.11+ (type hints kötelező, `from __future__ import annotations`)
- f-string használata
- Docstring minden publikus osztályon és metóduson
- Maximum 400 sor fájlonként; 200 felett bonts kisebb modulokra vagy `routes/` alatti szétválasztásra (a történeti `api.py/pipeline.py/llm_provider.py` kivételek, fokozatosan modularizálandók)
- Konstansok fájl tetején
- Import sorrend: stdlib → third-party → local
- Frontend: `escapeHtml` minden felhasználói szövegnél, `getAuthHeaders()` minden nem-public fetch-nél

### Osztálytervezés
- Dependency injection (paraméterben kapja meg a függőségeket)
- Frozen dataclass használata ahol lehetséges
- Enum használata értéknaplózáshoz
- Protocol interfészek határozzák meg a szerződéseket
- Discovery/Research: `DiscoveryEngineConfig` validált, `DiscoveryAgentRunner` + `AutonomousDiscoveryEngine` DI-vel

## 2. API endpoint szabályok

### Válasz formátum
```json
// Sikeres
{"status": "ok", "data": {...}}
// Lista
{"proposals": [...]} / {"cycles": [...]} / {"runs": [...]}
// Hiba
{"error": "error_type"}
```

### HTTP státuszkódok
- 200: Sikeres művelet
- 201: Létrehozás (`/api/research/sessions`, pipeline SPEC)
- 400: Hibás kérés (validálási hiba)
- 404: Nem található
- 409: Ütközés (pl. idempotencia)
- 500: Szerver hiba (gateway timeout is ide map-el)

### Security
- Bemeneti validálás minden POST endpointon (Pydantic / `field_validator`)
- XSS prevention (escapeHtml JavaScriptben)
- Security headers (X-Content-Type-Options, X-Frame-Options, CSP)
- Auth: `X-API-Key` / `Authorization: Bearer` + RBAC; public read-ek a `_PUBLIC_PATHS`-ben, írások `getAuthHeaders()`-től függenek
- LLM gateway: `http://127.0.0.1:8000/v1` lokális proxy, 120s timeout, `X-API-Key` is küldve

## 3. Tesztelési szabályok

### Teszt lefedettség
- Minden publikus metódusra legyen teszt
- Happy path + edge case + error case
- Mockoljuk a külső szolgáltatásokat (GitHub API, LLM API/gateway)
- Integrációs teszt a teljes láncra: `research → proposal → roadmap accept/develop → pipeline manifest + kanban`

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
# Összes teszt (pytest, hermes venv) — EZ A VALÓDI FUTTATÁS (nightly is ezt használja)
PATH=.venv/bin:$PATH pytest -q
# Unit csak
PATH=.venv/bin:$PATH pytest tests/unit -q 2>/dev/null || PATH=.venv/bin:$PATH pytest tests -q -k "unit"
# E2E (böngésző/HTTP)
PATH=.venv/bin:$PATH pytest tests/e2e -q
# Egyedi
PATH=.venv/bin:$PATH pytest tests/test_modul_név.py -q
# Szintaxis
python -m compileall -q control_plane tests
node --check control_plane/static/app.js
```
Megjegyzés: a `tests/` gyökérben vannak a unit tesztek (`test_*.py`), a `tests/e2e/` alatt a böngészős E2E-k. A `tests/unit/` mappa részleges — ha létező útvonalat írsz, azt használd.

## 4. Git szabályok

### Commit formátum
```
<scope>: <rövid leírás>

- Részletes leírás
- Miért kellett a változás
```

Példák:
- `feat: GitHub Issue → Auto Plan generálás`
- `fix: Idempotencia javítás webhook kezelésben`
- `test: Unit tesztek az IssueProcessorService-hez`
- `docs: API dokumentáció frissítés`
- `chore: Dead legacy code takarítás`

### Branch kezelés
- `main`: Stabil, production-ready (közvetlen commit + push a kis scope-ú fixeknél)
- `feature/<név>`: Nagyobb funkciók (opcionális)
- Minden commit előtt: `git diff --stat`, `python -m compileall -q`, `node --check` ha frontend érintett
- Push után: `git status --short` tiszta

## 5. Dokumentáció szabályok — döntések és kutatás (kötelező)

### ADR és research kötelezés
- `researcher` nem zárhat kártyát ADR nélkül: minden feature / nagyobb döntés → 1 `docs/decisions/ADR-NNN-{slug}.md` (max 1 oldal, template: `ADR-000-template.md`). `proposed → accepted` státusz, `docs/research/YYYY-MM-DD-*.md` linkkel.
- `researcher` nyers anyag: `docs/research/YYYY-MM-DD-{tema}.md` (max 5 oldal, **comparison table kötelező** ha több opció). Kanban comment csak linket tesz: "Research kész: docs/research/... → jóváhagyásra vár" + `kanban_block(kind=needs_human)`.
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
1. `python -m compileall -q control_plane tests` → Szintaktikai hiba nélkül
2. `node --check control_plane/static/app.js` ha frontend változott
3. `PATH=.venv/bin:$PATH pytest -q` vagy legalább a releváns `tests/unit` zöld
4. `git diff --stat` → Ellenőrzés

### Push előtt
1. `git pull --rebase` → Merge conflict nélkül (opcionális kis repo-nál)
2. `git push` → Sikeres
3. `git status --short` → Tiszta

### Átadás előtt
1. Teszt szám pontosság
2. Fájlnevek egyeznek a tervekkel
3. Nincs nem tervezett módosítás
4. Discovery: `GET /api/research/discovery-settings` 12 domain/12 keyword és `POST /api/research/sessions` E2E végigfut (proposal → roadmap → pipeline)

## 7. Discovery & Autonóm Pipeline specifikus

- `target_domains`/`search_keywords` nem csak tárolva, hanem `_mining_prompt`-ban is interpolálva legyen
- `Synthesis` kulcs case-insensitive (`synthesis`/`Synthesis`) kezelése `_proposal`-ban
- LLM gateway timeout 120s (nem 60s) — hosszú synthesis promptok miatt
- `research → proposal → roadmap → pipeline → kanban` lánc egyben tesztelendő, nem csak a részek
- `agy` → `agy -p`, `hermes` → `hermes chat -q --yolo` (nem `run` / `--profile -z`)
