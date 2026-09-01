# Swiss P Map Feature Brief Audit Report

**Dátum:** 2026-09-01  
**Módszertan:** RVAD 1.1, `METHODOLOGY.md` 3.1  
**Eredmény:** 30 brief, egységes sablon, szinkronizált registry

## Vizsgálati kör

Az audit a gyökér `METHODOLOGY.md` brief-szabályait, a `src/` és `frontend/src/` implementációt, az ADR-001–ADR-022 döntéseket, a `docs/research/` anyagokat, a master roadmapet, a meglévő briefeket és a registryt vetette össze.

## Meglévő briefek módosításai

- **BRIEF-001–BRIEF-020:** egységes H1 cím, külön metaadatsorok, kötelező fejezetnevek és konzisztens „Jelenlegi / Tervezett” story-fejezet.
- A rövid briefek legalább négy viselkedési nézőpontot kaptak: happy path, edge case, error/fallback és hozzáférhető GUI-használat.
- **BRIEF-001:** tisztázva a tényleges Three.js + FastAPI + jelenlegi SQLite architektúra és a PostGIS csak külön ADR-rel tervezett státusza.
- **BRIEF-005–009, 011–014:** pontosítva az élő, cache-elt és fallback adatok, upstream hibák, forráshűség és adatminőség felhasználói elvárásai.
- **BRIEF-015–018:** kiegészítve hozzáférhetőségi, input-validációs, mobil és hiányos adat peremfeltételekkel.
- **BRIEF-019–020:** kiegészítve a találat nélküli keresés, hibás export és részleges adatok kezelésével.

## Új briefek

- **BRIEF-021:** tematikus jelmagyarázat és forráslink, az ADR-019 és `MapLegend.tsx` alapján.
- **BRIEF-022:** determinisztikus kockázatjelzés és indoklás, az ADR-020 és `RiskBadge.tsx` alapján.
- **BRIEF-023:** sugár-figyelő UI, az ADR-018/021 és `WatchZone.tsx` alapján.
- **BRIEF-024:** megosztható URL-állapot, az ADR-022, `useShareableState.ts` és `ShareButton.tsx` alapján.
- **BRIEF-025:** mentett figyelési zónák és értesítések, a competitor research és a 20 napos Planning időablak alapján.
- **BRIEF-026:** kataszteri rétegválasztó és parcella-adatlekérdezés, a meglévő ÖREB/tematikus rétegképesség következő önálló terméklépéseként.
- **BRIEF-027:** offline PWA és gyenge hálózati mód mobil használatra.
- **BRIEF-028:** 2-5 körzet összehasonlítása normalizált, forrásolt mutatókkal.
- **BRIEF-029:** egységes adatforrás-, frissesség- és bizalmi állapot az élő/cache/fallback szolgáltatások fölött.
- **BRIEF-030:** mobil, billentyűzetes és akadálymentes használhatóság önálló keresztmetszeti képességként.

## Architekturális kapcsolatok

- **Frontend térképi UX:** BRIEF-003, 010, 013, 015, 021, 023, 024, 026, 030.
- **Planning adatút és térbeli motor:** BRIEF-002, 009, 014, 016, 018, 022, 023, 025.
- **Place és kataszteri adatok:** BRIEF-005, 007, 008, 011, 015, 026, 028, 029.
- **Politics és népszavazások:** BRIEF-005, 012, 017, 021, 028, 029.
- **Keresztmetszeti termékfunkciók:** BRIEF-004, 006, 019, 020, 024, 027, 029, 030.

## Fontos auditmegállapítások

1. Az ADR-019–ADR-022 képességei már kódszinten is megjelentek, de korábban nem volt saját briefjük. Ezt a BRIEF-021–024 megszünteti.
2. A kataszteri rétegváltó nem olvadt bele a BRIEF-015-be: a 015 a tematikus színezési motort fedi, a 026 a felhasználó által kapcsolható rétegkatalógust és parcella-identify folyamatot.
3. Az értesítések önálló briefet kaptak, de külön research/ADR nélkül nem tekintendők implementációra engedettnek.
4. A READY_FOR_SPEC státusz nem jelent SPEC_READY fejlesztési kaput. Az új FEAT-025–030 képességekhez a részletes specifikáció előtt research, kockázatértékelés és szükség szerint ADR kell.

## Registry-szinkron

A `docs/briefs/index.json` és `docs/briefs/README.md` ugyanabból a 30 briefből lett generálva. Az index tartalmazza a teljes darabszámot, fájlnevet, címet, státuszt és kapcsolódó feature/ADR értéket.
