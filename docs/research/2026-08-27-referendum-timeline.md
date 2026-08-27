# Research — Interaktív Történeti Szavazási Idővonal & Témaválasztó (Federal Referendum Selector)

- **Dátum:** 2026-08-27
- **Szerző:** System Architect & QA Lead
- **Státusz:** draft → ADR-017 alapja
- **Kapcsolódik:** `src/services/vote_service.py`, `src/models/vote.py`, `frontend/src/app/Map3D.tsx`, `ADR-012`
- **Kérdés:** Hogyan tehető interaktívvá a politikai réteg több évnyi és több témájú szövetségi népszavazás kiválasztására?

---

## 1. Elérhető Szövetségi Szavazási Témák (BFS VoteInfo API)

A VoteInfo OGD API-n keresztül azonnal elérhető előterjesztések:
1. **2024-11-24:**
   - *Nationalstrassen:* Autópálya-hálózat bővítése (Elutasítva: 47.3% Igen)
   - *Mietrecht Untermiete:* Bérleti jog szigorítása (Elutasítva: 46.2% Igen)
   - *EFAS / KVG:* Egészségbiztosítási finanszírozás egységesítése (Elfogadva: 52.8% Igen)
2. **2024-09-22:**
   - *Biodiversitätsinitiative:* Természet és tájvédelem (Elutasítva: 37.0% Igen)
   - *BVG-Reform:* Foglalkoztatói nyugdíjreform (Elutasítva: 32.9% Igen)
3. **2024-06-09:**
   - *Prämien-Entlastungs-Initiative:* Biztosítási prémiumok plafonja (Elutasítva: 44.5% Igen)
   - *Stromversorgung:* Megújuló energiatörvény (Elfogadva: 68.7% Igen)
4. **2024-03-03:**
   - *13. AHV-Rente:* 13. havi nyugdíj bevezetése (Elfogadva: 58.2% Igen)

---

## 2. A "Röstigraben" és Nyelvi Régiók Analitika

A svájci népszavazások jellegzetessége a nyelvi régiók közötti szavazati törésvonal:
- **Német Svájc (Deutschschweiz):** Pénzügyileg konzervatívabb magatartás.
- **Francia Svájc (Romandie):** Erősebb szociális és infrastruktúra-támogatás.
- **Olasz Svájc (Ticino):** Sajátos regionális prioritások.

---

## 3. Megvalósítási Terv

1. **`GET /api/v1/politics/votes/proposals` végpont:** Visszaadja az elmúlt szavazási napok listáját és témáit.
2. **`GET /api/v1/politics/votes/{proposal_id}` végpont:** Egy adott szavazás 26 kantonos adatait szolgáltatja.
3. **Frontend Selector Dropdown a 3D Térkép kártyáján:** A felhasználó egy kattintással átkapcsolhat a 13. AHV-Rente, a BVG-Reform vagy az Autópálya-bővítés szavazása között, és a kantonok azonnal átszíneződnek!
