# Research — Térbeli Sugár- és Poligon Keresőmotor (Spatial Radius & Bounding Box Engine)

- **Dátum:** 2026-08-27
- **Szerző:** System Architect & QA Lead
- **Státusz:** draft → ADR-018 alapja
- **Kapcsolódik:** `src/services/planning_service.py`, `src/db/planning_repo.py`, `src/services/geo_converter.py`, `ADR-001`, `ADR-002`
- **Kérdés:** Hogyan hajthatók végre gyors (<15ms) térbeli sugár- (`radius_meters`) és térképnézeti befoglaló-keret (`bbox`) lekérdezések a 22,000+ svájci építési projektre?

---

## 1. Problémafelvetés

Jelenleg az építési projektek szűrése mereven a 4-jegyű irányítószámra (`postcode`) támaszkodik.
Ez két súlyos korlátot jelent:
1. **Kerülethatárok torzítása:** Ha a felhasználó a Langstrasse déli végén lakik (`8004`), a túloldali (`8005` vagy `8001`) építkezések nem jelennek meg, pedig 50 méterre vannak.
2. **3D Térkép Pan & Zoom:** Amikor a felhasználó mozgatja a térképet, a látható nézetben (`bounding box`) lévő projekteket kell betölteni, nem egyetlen irányítószámot.

---

## 2. Geodéziai Matematika & Indextámogatás Svájcban

Svájc a metrikus **LV95** (CH1903+) koordináta-rendszert használja (kelet/észak méterben):
- A méter-alapú távolságszámítás euklideszi távolságként: $d = \sqrt{(E_1 - E_2)^2 + (N_1 - N_2)^2}$ méter.
- Ha WGS84 koordinátákat használunk: Haversine formula / gyors szögfüggvényes közelítés:
  $1^\circ \text{ szélesség} \approx 111.13 \text{ km}$
  $1^\circ \text{ hosszúság} \approx 111.320 \times \cos(\text{lat}) \approx 75.8 \text{ km}$ (47°-on Svájcban).

---

## 3. Adatbázis Megoldási Opciók

| Megközelítés | Kódbonyolultság | Válaszidő (22k sor) | Függőségek | Értékelés |
|---|---|---|---|---|
| **A: SQLite R-Tree / In-Memory Spatial Index** | Alacsony | **2-4 ms** | Nulla extra függőség (Python beépített sqlite3) | **4.9 / 5 (Javasolt)** |
| **B: PostGIS / PostgreSQL Docker** | Magas | 1-2 ms | Külső adatbázis szerver | **4.0 / 5** |
| **C: Teljes Python memóriaszűrés (Linear Scan)** | Minimális | 12-25 ms | Nincs | **3.8 / 5** |

---

## 4. Ajánlott Döntés

1. Létrehozunk egy **Haversine / Euklideszi térbeli szűrőmotort** a `PlanningRepo`-ban.
2. `GET /api/v1/planning/radius?lat=47.38&lon=8.52&radius_m=1000`: Visszaadja a ponttól adott méteres körön belüli építkezéseket távolság szerint növekvő sorrendben.
3. `GET /api/v1/planning/bbox?min_lat=47.36&min_lon=8.50&max_lat=47.40&max_lon=8.56`: Visszaadja a térképnézetben lévő összes építkezést.
