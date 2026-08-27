# Research — Országos Hely- és Körzetfeloldás (Federal Place Provider)

- **Dátum:** 2026-08-27
- **Szerző:** architect & QA lead
- **Státusz:** draft → ADR-011 alapja
- **Kapcsolódik:** `src/services/place_service.py`, `src/services/swisstopo_service.py`, `ADR-005`, `ADR-007`
- **Kérdés:** Hogyan skálázható a `place_service.py` a ZH pilot (8001, 8004) szintjéről az összes svájci irányítószámra (2200+ PLZ: Bern 3011, Basel 4001, Genf 1201, Uster 8610 stb.)?

---

## 1. Jelenlegi állapot és korlátok

Jelenleg a `place_service.py` csak a hardkódolt `_STUBS = {"8004": ..., "8001": ...}` szótárban szereplő irányítószámokat szolgálja ki.
Ha a felhasználó vagy a felület egy másik svájci PLZ-re (pl. Bern `3011`, Uster `8610`, Basel `4001`) kérdez rá:
```text
GET /api/v1/place/3011 -> 404 No data for postcode 3011
```
Ez a korábbi pilot szakaszból maradt benne, noha a Swisstopo és a szövetségi geo.admin API-k **teljes Svájc-lefedettséggel** rendelkeznek.

---

## 2. Élő mérések szövetségi rétegeken (2026-08-27 curl)

| Réteg / Végpont | Lekért Körzet | Eredmény | Megjegyzés |
|---|---|---|---|
| `SearchServer?searchText=3011&type=locations` | Bern (3011) | `lon: 7.448, lat: 46.947, LV95: 2600709, 1199563` | 100% Svájc lefedettség |
| `SearchServer?searchText=8610&type=locations` | Uster (8610) | `lon: 8.723, lat: 47.353, LV95: 2697014, 1245446` | Önkormányzat és kanton azonnal megvan |
| `Identify?layers=all:ch.are.gueteklassen_oev` | Bern (3011) | `klasse_de: "A - sehr gute Erschliessung"` | Országos ARE adat |
| `Identify?layers=all:ch.bfe.solarenergie-eignung-daecher` | Bern / Basel | Poligon és napsugárzási potenciál elérhető | BFE szövetségi kataszter |

---

## 3. Megoldási Architektúra

1. **Dinamikus Geokódolási Fallback:** Ha a PLZ nincs a lokális gyorstárban / stubban, a `place_service.py` a meglévő `swisstopo_service`-en keresztül lekéri a település nevét, kantonját és koordinátáit (`LV95` + `WGS84`).
2. **Szövetségi Identify rétegek lekérése:**
   - `ch.are.gueteklassen_oev` (ÖV-Güteklasse A–D)
   - `ch.bafu.larm-strassenlaerm_tag` (Zaj dB)
   - `ch.bfe.solarenergie-eignung-daecher` (Solar kWh/m²)
3. **Kanton-specifikus gazdagítás:**
   - Kanton ZH: `maps.zh.ch` ÖREB WFS és `steueramt.zh.ch` élő Steuerfuss.
   - Egyéb kantonok: alapadatok + szövetségi ÖV/Lärm/Solar megjelenítése tiszta fallbackkel.

---

## 4. Javaslat

- Készüljön el az **ADR-011** a szövetségi dinamikus helyfeloldásról.
- A `place_service.py` 400 soros korlátját betartva, a geokódoló logikát delegáljuk a `swisstopo_service.py`-ba.
