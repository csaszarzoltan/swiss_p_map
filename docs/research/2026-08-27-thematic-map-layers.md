# Research — Tematikus Térképi Hőtérkép & Rétegek (Sonnendach, Lärm, ÖREB 3D Vizualizáció)

- **Dátum:** 2026-08-27
- **Szerző:** System Architect & QA Lead
- **Státusz:** draft → ADR-015 alapja
- **Kapcsolódik:** `frontend/src/app/Map3D.tsx`, `src/services/place_service.py`, `ADR-003`, `ADR-007`, `ADR-010`
- **Kérdés:** Hogyan jeleníthető meg a felső menüpontok (Sonnendach, ÖREB, Lärm, Politik) váltásakor a 3D térképen egy dinamikus, vizuális hőtérkép/színkódolás anélkül, hogy elveszítenénk a 60 FPS sebességet és a sötét glassmorphism dizájnt?

---

## 1. Domain & Szövetségi Rétegek Elemzése

A svájci szövetségi GIS infrastruktúra (geo.admin.ch) WMS és vektoriális formátumban publikálja az alábbi rétegeket:
1. **Sonnendach (BFE):** `ch.bfe.solarenergie-eignung-dacher` — 0–1400+ kWh/m² / év besugárzási osztályok.
2. **Lärmbelastung (BAFU):** `ch.bafu.laerm-strassenlaerm_tag` — decibel kategóriák (<55 dB zöld, 55-65 dB sárga, >65 dB vörös).
3. **ÖREB Építési Zónák:** Nutzungsplanung / Bauzonen (Wohnzonen, Kernzonen, Mischzonen, Industrie).
4. **Politikai Népszavazási Támogatottság:** Igen szavazatok kantonális és körzeti hőtérképe (40% alatti bordó/piros, 50-60% ciánkék, 70%+ élénk kék/zöld).

---

## 2. Megvalósítási Technológiák Összehasonlítása

| Megközelítés | Teljesítmény (FPS) | Integráció a Three.js-be | Mobil kompatibilitás | Értékelés |
|---|---|---|---|---|
| **A: Dinamikus Shader / Vertex Color kanton-színezés** | **60 FPS** | Közvetlen Three.js Material `color.lerp` | Kiváló | **4.9 / 5 (Javasolt)** |
| **B: Swisstopo WMS Canvas Texture rávetítés** | 35-50 FPS | Dinamikus textúra csere Three.js síkra | Közepes (GPU memória) | **4.1 / 5** |
| **C: Teljes 2D MapLibre váltás** | 45 FPS | Külön 2D nézet (elveszik a 3D) | Jó | **3.5 / 5** |

---

## 3. Ajánlott Döntés (Hibrid Vertex Color & Shader kódolás)

Amikor a felhasználó kiválasztja a felső menü egy fülét:
- **`Politik` fül:** A kantonok és körzetek anyaga átvált a valós BFS népszavazási Igen/Nem hőtérképre (pl. Romandie 75% élénk kék, Innerschweiz 35% terrakotta).
- **`Sonnendach` fül:** A 3D modell arany/borostyánsárga szolár potenciál-térképre vált (1200+ kWh/m² izzó napfény tónus).
- **`ÖREB` fül:** Zónabesorolási színkódok (Kernzone lila, Wohnzone kék, Gewerbe narancs).
- **`Ort / Lärm` fül:** Zajterhelési háló (zöld/sárga/piros izofonák).

A váltás GSAP animációval, 0.4s alatt fokozatosan fuzionál, megőrizve a 60 FPS sebességet.
