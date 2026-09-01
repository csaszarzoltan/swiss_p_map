# BRIEF-001: Svájci Térinformatikai Architektúra és Stack

**Státusz:** READY_FOR_SPEC  
**Kapcsolódó feature:** FEAT-001 (ADR-001)  
**Forrás:** a meglévő Python FastAPI backend, Next.js 14 frontend, Three.js 3D térképi motor és geodéziai LV95/WGS84 transzformációk alapján

## Probléma

A svájci ingatlan-, kataszteri és politikai adatok heterogének, különböző koordináta-rendszerekben (LV95 EPSG:2056 vs. WGS84 EPSG:4326) és formátumokban érhetők el. A felhasználók számára hiányzik egy egységes, azonnali (<100ms) reakcióidejű, interaktív 3D-s felület, amely ötvözi a modern webes technológiát és a szigorú típusbiztonságot.

## Célcsoport és kontextus

Svájci ingatlanbefektetők, lakásvásárlók, helyi lakosok és önkormányzati elemzők, akik modern böngészőből szeretnének térbeli információt lekérdezni.

## Kívánt eredmény

Egy modern, típusbiztos és gyors webes alkalmazás, amely Three.js 3D felülettel és FastAPI REST végpontokkal rendelkezik, automatikus geodéziai koordináta-transzformációt biztosít, és megfelel a svájci adatvédelmi és minőségi elvárásoknak.

## Jelenlegi funkciókat lefedő felhasználói történetek

- **US-001-01:** Látogatóként szeretném az alkalmazást gyorsan megnyitni a böngészőmben, hogy azonnal interaktív svájci 3D térképet kapjak.
- **US-001-02:** Felhasználóként szeretném, hogy az LV95 és WGS84 koordináták automatikusan átválthatók legyenek a térképi megjelenítéshez.
- **US-001-03:** Rendszerként szeretném, hogy a backend Pydantic modellekkel és FastAPI végpontokkal garantálja a típushelyességet és a 0-hiba működést.

## Scope

- Next.js 14 (App Router) + TypeScript frontend.
- FastAPI + Python 3.11+ típusos backend.
- LV95 ↔ WGS84 konverter matematikai formulákkal (`geo_converter.py`).
- Szigorú linter és minőségkapu (mypy strict, ruff, pytest).

## Non-scope

- Felhasználói bejelentkezés / regisztráció (a rendszer publikus, nyílt adatokra épül).
- Fizetési átjáró (egyelőre open-access OGD).

## Érintett rendszerek

- `src/main.py`, `src/services/geo_converter.py`, `src/models/`
- `frontend/src/app/`, `frontend/src/lib/api.ts`

## Bizonytalanságok

- A nagyméretű térképi poligonok memóriaterhelése mobil eszközökön (optimalizálás szükséges).
