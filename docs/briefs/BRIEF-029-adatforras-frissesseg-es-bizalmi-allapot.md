# BRIEF-029: Adatforrás, Frissesség és Bizalmi Állapot

**Státusz:** READY_FOR_SPEC  
**Kapcsolódó feature:** FEAT-029  
**Forrás:** meglévő live/fallback integrációk és auditkövetelmény

## Probléma
A felület élő, cache-elt, beágyazott és fallback adatokat vegyesen használ, de ezek eredete és frissessége nem minden nézetben egyértelmű.

## Célcsoport és kontextus
Minden felhasználó, különösen elemzők és döntéshozók, amikor az adatok alapján következtetést vagy jelentést készítenek.

## Kívánt eredmény
Minden lényeges adatmezőhöz konzisztens source, fetched_at, valid_for és quality_state metaadat tartozik, amely a UI-ban érthetően megjelenik és exportba is bekerül.

## Jelenlegi / Tervezett funkciókat lefedő felhasználói történetek
- **US-029-01:** Felhasználóként szeretném látni egy adat hivatalos forrását és utolsó frissítését.
- **US-029-02:** Felhasználóként szeretném megkülönböztetni az élő, cache-elt, fallback és nem elérhető adatot.
- **US-029-03:** Elemzőként szeretném, hogy a forrás- és frissességi metaadat az exportban is szerepeljen.
- **US-029-04:** Felhasználóként szeretném, hogy schema drift vagy sikertelen frissítés esetén a régi adat ne jelenjen meg frissként.

## Scope
- Egységes provenance modell és UI badge/tooltip.
- API és export kompatibilis metaadat, upstream hibaállapot.

## Non-scope
- Az upstream adatok tartalmi hitelesítése vagy jogi garancia vállalása.

## Érintett rendszerek
- src/models és provider service-ek
- FastAPI válaszmodellek
- frontend DetailPanel/TopicList/MapLegend
- BRIEF-020 export

## Bizonytalanságok
- Visszafelé kompatibilis API-séma, időzónák, forrás-specifikus frissítési ciklusok.
