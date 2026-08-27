# Research — Építési Projektek Részletező & Kockázatelemző Panel (Baugesuch Deep Inspector)

- **Dátum:** 2026-08-27
- **Szerző:** System Architect & QA Lead
- **Státusz:** draft → ADR-016 alapja
- **Kapcsolódik:** `src/models/planning.py`, `src/services/planning_service.py`, `frontend/src/app/[locale]/page.tsx`, `ADR-002`, `ADR-009`, `ADR-013`
- **Kérdés:** Milyen mélységű adatstruktúrára van szüksége egy svájci ingatlanbefektetőnek, helyi lakosnak vagy építésznek, amikor egy kiválasztott Baugesuch (építési engedély) adatait vizsgálja?

---

## 1. Hivatalos Svájci Építési Adatok Elemzése (Amtsblatt / OGD 2982)

Az OGD 2982 CSV és a szövetségi Amtsblattportal XML a következő kulcsmezőket tartalmazza:
1. **Építtető & Tervező (Akteure):**
   - `buildingContractor_company_legalForm_de` / Cég neve / Címe.
   - `projectFramer_company_legalForm_de` / Építész iroda neve.
2. **Kataszteri & Zónabesorolási Horgonyok:**
   - `districtCadastre_relation_cadastre` — Helyrajzi szám (Parzellen-Nr. / Assek. Nr.).
   - `districtCadastre_relation_buildingZone` — ÖREB Zóna (pl. `W3` Háromszintes lakóövezet, `K` Kernzone).
3. **Jogi Határidők & Einsprache:**
   - `publicationDate` — Közzététel napja.
   - `auflage_end` — 20 napos fellebbezési határidő vége.
   - `entryDeadline` — Hivatalos beadványi határidő.

---

## 2. Kockázatelemzési Logika (Risk Engine)

A rendszer szabályalapú és AI-támogatott kockázatelemzést végez az építkezés típusáról:
- **Magas kockázat (Piros jelvény):** Tetőtér-beépítés / Magasságemelés védett övezetben (`Kernzone` / `Denkmalschutz`) vagy határidőhöz közeli (< 5 nap van hátra).
- **Közepes kockázat (Sárga jelvény):** Új építés kereskedelmi zónában, zajvédelmi határérték közelében.
- **Alacsony kockázat (Zöld jelvény):** Homlokzat-felújítás, belső átépítés vagy napelemes tetőtelepítés.

---

## 3. Megvalósítás

1. **`BaugesuchDetail` Pydantic modell:** Kibővített mezőkkel (vállalkozó, építész, helyrajzi szám, zóna, kockázati szint, fennmaradó napok).
2. **Frontend Deep Inspector Drawer:** Ha a felhasználó a 3D térképen vagy a listában rákattint egy projektre, egy elegáns, lebegő oldalpanel nyílik meg a teljes dossziéval, közvetlen Amtsblatt hivatkozással és fellebbezési segédlettel.
