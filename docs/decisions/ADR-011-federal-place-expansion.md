# ADR-011: Országos Hely- és Körzetfeloldás (Federal Place Provider)

- **Dátum:** 2026-08-27
- **Státusz:** accepted
- **Szerző:** architect & QA lead (research: `docs/research/2026-08-27-federal-place-expansion.md`)
- **Kanban:** #swiss-p-map-011

## Kontextus
A Swiss P Map eddigi fázisai a zürichi pilotra (8001, 8004) fókuszáltak, ezért a `place_service.py` a nem zürichi irányítószámokra (pl. Bern `3011`, Basel `4001`, Uster `8610`, Genf `1201`) 404-es hibát adott. A Swisstopo geokódoló és a szövetségi geo.admin rétegek (ARE ÖV, BAFU Zaj, BFE Napsugárzás) azonban egész Svájcban elérhetők.

## Döntés
1. **Dinamikus Swisstopo koordináta-feloldás:** Ha egy 4-jegyű svájci PLZ nem szerepel a beépített gyorstárban, a rendszer a Swisstopo `SearchServer` végpont segítségével dinamikusan meghatározza a települést, kantont és az LV95/WGS84 koordinátákat.
2. **Országos szövetségi adatok (Identify):** A koordináták birtokában a `place_service` automatikusan lekéri az országos ARE ÖV-osztályt, a BAFU zajterhelést és a BFE tetőpotenciált.
3. **Kantonális differenciálás:** A zürichi specifikus rétegek (ZH ÖREB WFS, ZH Steuerfuss) csak `canton == 'ZH'` esetén futnak, más kantonokban transzparens `None` fallback lép érvénybe hibadobás nélkül.
4. **400 soros limit megőrzése:** A geokódolási segédfüggvények a `src/services/swisstopo_service.py`-ban kapnak helyet, elkerülve a `place_service.py` túlméretezését.

## Elvetve
| Opció | Miért nem |
|---|---|
| 2200 PLZ manuális beégetése kódban | Karbantarthatatlan, feleslegesen növeli a kódméretet |
| Minden kantonra külön WFS építése most | Túl nagy scope, fokozatosan bővítendő |

## Következmény
- Bármely svájci PLZ keresésekor azonnal megjelennek a valós helyi mutatók (ÖV, Zaj, Solar).
- A Quick-Pick gombok (`3011 Bern`, `4001 Basel`, `8610 Uster`) élőben működnek.
- Mock tesztek bővítése az új kantonokra és koordináta-feloldásra.

## Kapcsolódó
- Research: `docs/research/2026-08-27-federal-place-expansion.md`
- Kód: `src/services/place_service.py`, `src/services/swisstopo_service.py`
- Következő ADR: ADR-012 (ÖREB Kataster M2M Országos Kiterjesztés)
