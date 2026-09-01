# BRIEF-020: Export és Ingatlanfejlesztői Audit Csomag

**Státusz:** READY_FOR_SPEC  
**Kapcsolódó feature:** FEAT-020  
**Forrás:** a körzeti és építési dossziék strukturált exportálási igénye, nyomtatási és PDF/JSON riport-készítés alapján

## Probléma

A felhasználók és befektetők az összegyűjtött körzeti információkat (Steuerfuss, zaj, napenergia, ÖREB zóna, aktív és történeti építkezések, parlamenti képviselők, AI összefoglaló) szeretnék elmenteni, kollégákkal megosztani vagy egy ingatlanfejlesztési döntés-előkészítő dokumentációhoz csatolni.

## Célcsoport és kontextus

Ingatlanfejlesztők, banki hitelbírálók, építészek és tudatos ingatlanvásárlók.

## Kívánt eredmény

Egyetlen kattintással letölthető, professzionálisan formázott körzeti audit csomag (PDF összefoglaló és géppel olvasható JSON/CSV export).

## Jelenlegi / Tervezett funkciókat lefedő felhasználói történetek

- **US-020-01:** Felhasználóként szeretném a keresett körzet teljes profilját egy strukturált JSON fájlban letölteni.
- **US-020-02:** Felhasználóként szeretném az aktív építési engedélyek listáját CSV formátumban exportálni táblázatkezelőhöz (Excel).
- **US-020-03:** Felhasználóként szeretnék egy tiszta, nyomtatóbarát PDF összefoglaló nézetet kapni a körzet összes mérőszámáról és a 3D térképi pillanatképről.

- **US-020-04:** Felhasználóként szeretném, hogy részleges adat vagy exporthiba esetén a rendszer jelezze a hiányt, és ne állítson elő félrevezető auditcsomagot.

## Scope

- Export vezérlőgombok a részletező panelen.
- `GET /api/v1/place/{postcode}/export?format=json|csv` végpont.
- Nyomtatóbarát CSS stíluslapok a böngészős PDF mentéshez.

## Non-scope

- Fizetős API számlázási rendszer és vízjelezés.

## Érintett rendszerek

- `src/main.py`, `src/services/place_service.py`, `frontend/src/components/DetailPanel.tsx`

## Bizonytalanságok

- Különböző böngészők natív PDF nyomtatási motorjainak tipográfiai eltérései.
