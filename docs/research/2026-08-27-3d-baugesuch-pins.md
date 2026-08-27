# Research — 3D Építési Projektek & Interaktív Markerek (3D Baugesuch Pins)

- **Dátum:** 2026-08-27
- **Szerző:** architect & QA lead
- **Státusz:** draft → ADR-013 alapja
- **Kapcsolódik:** `frontend/src/app/Map3D.tsx`, `src/services/ogd_service.py`, `ADR-003`, `ADR-009`
- **Kérdés:** Hogyan jeleníthetők meg a 22,000+ építési projekt (Baugesuch) adatai közvetlenül a 3D Three.js térképen interaktív, kattintható markerek formájában?

---

## 1. Jelenlegi probléma

Az adatbázisban a 22,000 zürichi építési engedély (OGD 2982) jelen van, de a CSV import `lat` és `lon` mezőket üresen hagyta (`None`).
Emiatt a `Map3D.tsx` `pinGroup` szűrője (`if (b.lat == null) continue;`) kiszűrte a projektek 99%-át, így a térképen csak a 2 beégetett demo pin jelent meg.

---

## 2. Koordináta Kiosztás & Megjelenítés

1. **Koordináta Geokódolás / Centroid szórás:**
   - A `projectLocation_address_swissZipCode` alapján meghatározzuk a PLZ központi koordinátáját (`POSTCODE_WGS84`).
   - Egy determinisztikus eltolási függvénnyel (az építési cím és ID hash-e alapján: `±0.005°` sugarú körben) minden építési engedély valós koordinátát kap a település/körzet utcahálózatán belül.
2. **3D Pin Felépítés:**
   - Hengeres oszlop + lüktető arany/borostyán gömbkorona (`#f59e0b` / `#fbbf24`).
   - Alapjánál finom pulzáló gyűrű jelzi az aktív 20 napos fellebbezési időszakot (`Auflagefrist`).
3. **Interaktivitás:**
   - Kattintásra a Three.js Raycaster azonosítja a kiválasztott projektet, és a kamera fókuszál az építkezésre.
