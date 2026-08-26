# ADR-003: 3D sematikus Svájc-térkép — Three.js + GSAP (szürke hasábok, hover & drill-down)

- **Dátum:** 2026-08-26
- **Státusz:** accepted
- **Szerző:** analyst (research: `docs/research/svajc_3d_terkep.html` — 675 sor single-file prototype)
- **Kanban:** t_add5150f folytatása (Planning pillér mellett párhuzamos frontend kártya)

## Kontextus

A `Map.tsx` (MapLibre Swisstopo Light) fehér maradt élesben (screenshot 2026-08-26), a korábbi `curl | grep` ellenőrzés nem fogta meg — csak a Playwright E2E (3. javítás, `3ebb992`) tette láthatóvá. A felhasználó nem 2D csempetérképet akar, hanem **sematikus, szürke 3D Svájc-modellt**: 26 kanton hasábként, hover-re kivilágosodik/kiemelkedik, kattra bezoomol kanton → város szintre, ott Place/Politics/Planning panel. A `docs/research/svajc_3d_terkep.html` prototype ezt 1:1 bizonyítja (Three r128 + OrbitControls + GSAP, 26 kanton + Zürich 6 város, 3 szintű drill-down).

## Döntés

- **Stack: Three.js ESM (`three@0.160`) + `three/addons/controls/OrbitControls.js` + `gsap@3.12` vanilla `useEffect`-ben** (`frontend/src/app/Map3D.tsx`, `ssr: false` dynamic). A prototype `r128` CDN-global → ESM-re cserélve, TS-sel. Nem R3F/drei — kisebb bundle, direkt portolható a működő prototype-ból.
- **Vizuál — a példa marad, színekre rám bízva:** sötét `radial-gradient #030712 → #111827` háttér, `GridHelper` + `FogExp2`, alap üveg `0x1e293b` (`roughness 0.1`, `opacity 0.42`), hover: `gsap y +0.65` + `color #38bdf8` + `emissive #0284c7` + edge `opacity 0.95`. Sötétet választom világos szürke helyett — 3D-ben sokkal jobb a mélység, a hover így is "szürkéből kivilágosodás" hatású.
- **Adat MVP: a prototype 26 kanton + Zürich 6 város sematikus poligonjai** (`SWISS_CANTONS` konstans, `docs/research/svajc_3d_terkep.html`-ből kiemelve → `frontend/src/app/swissCantons.ts`). Valódi `swisstopo swissBOUNDARIES3D` GeoJSON + `d3-geo` vetítés külön ADR-004 (nem blokkolja az MVP-t).
- **Interakció 1:1 a példából:** `Raycaster` hover (tooltip követi az egeret), 3 szint (`selectedCanton`/`selectedCity` állapotgép), `gsap 1.3s/1.1s` kamera `Box3.getCenter`-re, többi `opacity 0.08`-ra halványul, `handleBack()` + breadcrumb (`SVÁJC / ZÜRICH / …`), glassmorphism panel (`vote-bar`, `stat-*`).
- **Integráció:** `page.tsx` a `Map` helyett `Map3D`-t renderel (`dynamic ssr:false`), város-kattra a meglévő `SearchPanel` panel logikája bővíthető `postcode → /api/v1/place` + `/politics` hívással (külön kártya, nem ebben a lépésben).

## Elvetve

| Opció | Miért nem |
|---|---|
| React Three Fiber + drei | Nagyobb absztrakció, a működő vanilla prototype-ot kellene újraírni — nincs nyereség MVP-ben |
| MapLibre `fill-extrusion` 3D réteg | Maradna a fehér csempe-probléma, nem ad sematikus "hasáb" kontrollt |
| SVG 2.5D izometrikus (GSAP nélkül) | Nincs valódi 3D mélység, a kért OrbitControls forgatás/zoom nem megoldható |

## Következmény

- **Kártyák:** `Map3D.tsx` scaffold → hover highlight → click drill-down → város-katt backend bekötés (külön) → E2E `map-3d` canvas. Max 400 sor/file, `data-testid="map-3d"` / `map-container`.
- **Developer:** `three` + `gsap` `frontend/package.json`-ba, `swissCantons.ts` ≤400 sor, `Map.tsx` megmarad fallbacknek de nem rendereljük. Minden hiba `data-testid="map-error"`-ban látszik (nem néma fehérség).
- **Validálás:** `npm run build` zöld, `npx playwright test` 3/3 (white-screen regresszió most `map-3d` canvas-ra), élő `http://localhost:3310` — kanton hover kiemelkedik, katt zoomol.

## Kapcsolódó

- Research: `docs/research/svajc_3d_terkep.html` (single-file prototype, 26 kanton)
- Terv: `docs/plans/2026-08-26-planning-pillar-phase2.md` Task 4 (frontend markerek) → 3D-ben teljesül
- Kód: `frontend/src/app/Map3D.tsx`, `frontend/src/app/swissCantons.ts`
- Következő ADR: ADR-004 (valódi GeoJSON + d3-geo vetítés)
