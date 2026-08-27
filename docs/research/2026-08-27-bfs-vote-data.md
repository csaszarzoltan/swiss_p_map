# Research — Valós Szövetségi Szavazási Adatok (BFS / FSO Vote Data API)

- **Dátum:** 2026-08-27
- **Szerző:** architect & QA lead
- **Státusz:** draft → ADR-012 alapja
- **Kapcsolódik:** `src/services/vote_service.py`, `src/models/vote.py`, `ADR-003`, `ADR-005`
- **Kérdés:** Hogyan integrálható a svájci Szövetségi Statisztikai Hivatal (BFS/FSO) hivatalos népszavazási adatfolyama, hogy a 3D térképen mind a 26 kanton valós szavazati arányokkal, részvétellel és 4-nyelvű szavazási címekkel jelenjen meg?

---

## 1. Forrás és API Struktúra

A svájci állam hivatalos nyílt adatforrása a **VoteInfo OGD webszolgáltatás** (`https://ogd-static.voteinfo-app.ch/v1/ogd/sd-t-17-02-{YYYYMMDD}-eidgAbstimmung.json`).
Ez a fájl tartalmazza:
- Az adott szavazási nap összes szövetségi előterjesztését (`vorlagen`).
- Címeket mind a 4 hivatalos nyelven (`de`, `fr`, `it`, `en`).
- Nemzeti szintű összesítést (`schweiz`).
- Kantonális szintű eredményeket mind a 26 kantonra (`kantone`, BFS azonosító 1..26).
- Önkormányzati / községi szintű bontást (`gemeinden`).

---

## 2. Élő Adatminták (2024-es népszavazások)

| Dátum | Kiemelt Előterjesztés | Svájci Igen % | Zürich Igen % | Bern Igen % | Vaud Igen % | Appenzell I. Igen % |
|---|---|---|---|---|---|---|
| **2024-03-03** | 13. AHV-Rente (13. havi nyugdíj) | **58.2%** | 52.1% | 56.3% | 74.4% | 31.5% |
| **2024-09-22** | BVG-Reform (Nyugdíjreform) | **32.9%** (Elutasítva) | 35.8% | 33.1% | 27.2% | 39.1% |
| **2024-11-24** | Nationalstrassen (Autópálya-bővítés) | **47.3%** (Elutasítva) | 43.1% | 46.5% | 39.8% | 59.2% |

---

## 3. BFS Kanton Kódolás (1..26)
```python
BFS_CANTON_MAP = {
    1: "ZH", 2: "BE", 3: "LU", 4: "UR", 5: "SZ", 6: "OW", 7: "NW", 8: "GL",
    9: "ZG", 10: "FR", 11: "SO", 12: "BS", 13: "BL", 14: "SH", 15: "AR", 16: "AI",
    17: "SG", 18: "GR", 19: "AG", 20: "TG", 21: "TI", 22: "VD", 23: "VS", 24: "NE",
    25: "GE", 26: "JU"
}
```

---

## 4. Megvalósítási Terv

1. **`VoteService` létrehozása:** Beolvassa a legfrissebb szövetségi szavazás JSON-ját (offline beágyazott gyorstár + online frissítés lehetőség).
2. **REST Végpont:** `GET /api/v1/politics/votes/latest` szolgáltatja a szövetségi és kantonális bontást.
3. **3D Térkép Integráció:** A `Map3D.tsx` és `swissCantons.ts` a valós `yes` százalékokat mutatja kanton-föléhúzáskor.
