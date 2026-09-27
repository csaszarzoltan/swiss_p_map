# Következő lépés — részletes követelmény (Cloud Code-nak)

> **Handoff:** `docs/handoffs/cloud-code-handoff-2026-09-24.md` · **Választott opció: A — Frontend E2E + PWA + Export bezárása**
> Dátum: 2026-09-24 · Szerző: Hermes Agent · Státusz: SPEC_READY → kanban

---

## 1. Miért pont ez?

A v0.3.0 után a legnagyobb kockázat a **frontend regresszió**: 10 SPEC (003/004/010/013/015/020/021/024/031/044) + 3 `assert True` placeholder (025/027/030) **teszt nélkül** van. A backend 238 passed / 91 mypy clean, az E2E csak 8/8 happy-path — egy rossz merge csendben töri a 3D-t, az i18n-t vagy a PWA-t. Az A opció ezt zárja, mielőtt új élő integrációkat (B) nyitnánk.

**Pontozás:** A=15 > C=14 > B=12 (érték×költség×kockázat×karbantarthatóság).

---

## 2. Scope — 3 kártya, láncolva (hotspot-ütközés miatt)

### Kártya A1: 3D + i18n + menü E2E (SPEC-003/004/010/013/015/021/024/031/044)

**Cél:** a 10 NONE SPEC mindegyikéhez legalább 1 Playwright-teszt, amely valós böngészőben bizonyítja a feature-t (nem `assert True`).

| SPEC | Mit kell bizonyítani | E2E forgatókönyv (Given/When/Then) |
|------|---------------------|-------------------------------------|
| 003 | 3D térkép 26 kantonnal, `Map3D.tsx` canvas 200×200+ | `goto /de` → `map-3d` + `canvas bbox >200` + `N iránytű` látható |
| 004 | 4 nyelv (DE/EN/FR/IT) hreflang + LanguageSwitcher | `goto /de` → `LanguageSwitcher` → váltás `en` → URL `/en` + hero szöveg vált |
| 010 | TopicSidebar + DetailPanel (6 menüpont) | `topic-sidebar` + `menu-overview/politik/ort/planung/solar/oereb` látható, kattintás → panel vált |
| 013 | 3D Baugesuch pin (amber pulse) + Einsprachefrist | PLZ `8004` keresés → pin megjelenik + `days_left` badge |
| 015 | Tematikus rétegek (heat layer) | témaváltás → `canvas` újrarajzol + `MapLegend` paletta vált |
| 021 | MapLegend + forráshivatkozás | `MapLegend` komponens látható, `source`/`trust_state` link |
| 024 | Megosztható deep-link (locale-aware) | `ShareButton` → vágólap → URL tartalmaz `plz/topic/lang` |
| 031 | Tavak + alpesi domborzat (ha van 3D terrain) | `map-3d` terrain réteg látható vagy `source_pending` jelzés |
| 044 | Glassmorphism HUD / design token | vizuális smoke: header + hub `backdrop-blur` osztály jelenléte |
| 027 | PWA online/offline jelzés | `PwaStatus` `Online`/`Offline` + `role=status` + `aria-live` |

**Fájlok:** `frontend/e2e/a1-frontend-coverage.spec.ts` (új) — **additív**, meglévő `app.spec.ts`-t nem módosít.
**Kapuk:** `npx playwright test e2e/a1-frontend-coverage.spec.ts` zöld, meglévő 8/8 nem törik.
**Max 3 file/lépés**, TDD RED→GREEN.

### Kártya A2: PWA offline + Export audit-csomag (SPEC-027/020)

**Cél:** a két placeholder SPEC-et valódi implementációvá emelni.

**SPEC-027 — PWA offline:**
- `public/sw.js` service worker: `install` → cache shell (`/de`, `/manifest.json`, statikus assetek), `fetch` → cache-first navigációra, network-first API-ra.
- `manifest.json` kiegészítése: `icons` (min. 192×192 + 512×512, generált placeholder PNG is elég), `scope`, `start_url`.
- Teszt: `navigator.serviceWorker.ready` + offline szimuláció (`page.route` abort) → `PwaStatus` `Offline · Cache` + `aria-live`.

**SPEC-020 — Export audit-csomag:**
- `GET /api/v1/place/{postcode}/export?format=json|csv` — összegyűjti az adott PLZ-hez tartozó összes élő adatot (place, solar, ÖREB, Steuerfuss, planning) + `source`/`fetched_at`/`trust_state` provenience-szel, `Content-Disposition: attachment`.
- CSV: fejléces, `;` elválasztó (svájci konvenció), JSON: `{postcode, sources[], data{}}`.
- `DetailPanel` → "Export" gomb (`data-testid="export-button"`), `format` választó (JSON/CSV), `a11y` billentyűzettel elérhető.
- Teszt: unit (service) + API (TestClient, `format` 422, ismeretlen PLZ 404) + E2E (gomb katt → letöltés).

**Fájlok:** `src/services/export_service.py` (új), `public/sw.js` (új), `public/manifest.json` (módosítás), `frontend/src/components/DetailPanel.tsx` (export gomb), `tests/unit/test_export_service.py` + `tests/e2e/test_export_api.py`, `frontend/e2e/a2-pwa-export.spec.ts`.
**Kapuk:** `pytest`, `mypy`, `ruff`, `tsc+build`, `8/8 + új E2E` zöld.
**Láncolás:** A2 csak A1 után indulhat (közös hotspot: `frontend/e2e/*`, `src/main.py` wiring).

### Kártya A3: Placeholder-csere + SPEC-státusz szinkron + release-higiénia

**Cél:** a 3 `assert True` (`tests/e2e/test_final_roadmap_api.py:54,58,62` → SPEC-025/027/030) cseréje valódi kontraktusra, + `docs/specs/SPEC-*.md` `implementationStatus: IMPLEMENTED` szinkron, + CHANGELOG `[Unreleased]` + README frissítés.

- SPEC-025 (mentett figyelési zónák): `GET /watch/zones` lista + `POST /watch/zones` round-trip kontraktus (már él — csak teszt kell).
- SPEC-027: PWA-teszt A2-ből (itt csak a placeholder cseréje).
- SPEC-030 (mobil/a11y): viewport `375px` + `axe`-lite (billentyűzet-tab + `aria-*` smoke).
- `docs/specs/SPEC-{003,004,010,013,015,020,021,024,027,030,031,044}.md` frontmatter + 1. fejezet `IMPLEMENTED`.
- `docs/audits/SPEC-coverage-2026-09-23.md` → új mérés (cél: 0 NONE).

**Láncolás:** A3 csak A2 után.

---

## 3. API-kontraktus (új)

```
GET /api/v1/place/{postcode}/export?format=json|csv
  200 json: {postcode, fetched_at, sources: [{source, fetched_at, trust_state}], data: {place, solar, oereb, steuerfuss, planning}}
  200 csv:  text/csv; charset=utf-8, Content-Disposition: attachment; filename="swiss-p-map-{postcode}.csv"
  422 format ∉ {json,csv}
  404 ismeretlen PLZ (nincs seed + nincs live feloldás)
```

PWA: nincs új API — `GET /sw.js` + `GET /manifest.json` statikus.

---

## 4. i18n-kulcsok (új)

```
pwa.status.online / pwa.status.offline  (de: Online / Offline · Cache, en: Online / Offline · Cached, fr/it uo.)
export.button / export.format.json / export.format.csv / export.toast.success
```

Meglévő `messages/{de,en,fr,it}.json` bővítése — additív.

---

## 5. Definition of Done

- [ ] A1: 10 SPEC × 1 E2E zöld, meglévő 8/8 nem törik
- [ ] A2: `sw.js` + `manifest.json` + `GET /export` (json+csv) + DetailPanel export-gomb + tesztek zöldek
- [ ] A3: 3 placeholder → valódi kontraktus, SPEC-státuszok szinkronban, audit 0 NONE
- [ ] Kapuk: `238+ passed` (A1/A2-vel nő), `mypy 91+ clean`, `ruff clean`, `tsc+build SSG`, `8/8 + új E2E` zöld
- [ ] `git log` + `CHANGELOG [Unreleased]` + `README` verzió/endpoint-szám frissítve
- [ ] `git push` mindhárom kártyán

---

## 6. Kockázatok

- **Hotspot-ütközés:** `src/main.py`, `frontend/src/lib/api.ts`, `DetailPanel.tsx`, `messages/*.json` — ezért láncolt kártyák, nem párhuzamos.
- **PWA cache:** `sw.js` ne cache-elje az API-t agresszíven (network-first API-ra, cache-first csak shell).
- **CSV separator:** `;` + `de-CH` tizedes `,` vs `.` — a CSV-ben `.` marad (gépi), a UI-ban lokalizált.

---

*Következő lépés: Cloud Code válasszon (A/B/C vagy D), majd hozza létre a kártyákat `hermes kanban create` + `boards list | grep ●` ellenőrzéssel.*
