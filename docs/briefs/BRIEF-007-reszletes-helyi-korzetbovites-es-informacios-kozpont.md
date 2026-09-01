# BRIEF-007: Részletes Helyi Körzetbővítés és Információs Központ

**Státusz:** READY_FOR_SPEC  
**Kapcsolódó feature:** FEAT-007 (ADR-007)  
**Forrás:** a 6 csempés helyi információs panel (Steuerfuss, Lärm, ÖV, Sonnendach, ÖREB zóna, GWR épületállomány) és a szövetségi rétegek alapján

## Probléma

A körzeti adatok felületén korábban csak 3 alapérték (adó, zaj, tömegközlekedés) látszott, elhanyagolva az energetikai napenergia-potenciált (BFE Sonnendach), az ÖREB zónabesorolást (Nutzungsplanung) és a szövetségi épületregisztert (GWR).

## Célcsoport és kontextus

Környezettudatos lakástulajdonosok, napelem-telepítők és építési telek után kutató magánszemélyek.

## Kívánt eredmény

Egy strukturált, 6 csempéből álló interaktív információs központ a "Hely" (Ort) fül alatt, amely kattintásra feltárja az egyes területek mélyebb adatait és forrásait.

## Jelenlegi / Tervezett funkciókat lefedő felhasználói történetek

- **US-007-01:** Felhasználóként szeretném megnézni a tetőmre eső éves napelemes besugárzást (pl. "1208 kWh/m² · Klasse Sehr gut").
- **US-007-02:** Felhasználóként szeretném tudni a körzet kataszteri zónáját (pl. "Kernzone", "Wohnzone W3").
- **US-007-03:** Felhasználóként szeretném látni a körzetben található regisztrált épületek számát a szövetségi GWR adatbázis alapján.
- **US-007-04:** Felhasználóként rákattintva egy csempére, a lenti panelen részletes magyarázatot és forrásmegjelölést szeretnék kapni.

## Scope

- `PlaceInfo` modell bővítése (`solar_kwh_m2`, `solar_class`, `oereb_zone`, `gwr_building_count`).
- 6 csempés grid a `TopicList.tsx` komponensben.
- Lokalizált magyarázó szövegek mind a 4 nyelven.

## Non-scope

- Egyedi épülettervek raszteres PDF letöltése a kataszterből.

## Érintett rendszerek

- `src/models/place.py`, `src/services/place_service.py`, `frontend/src/components/TopicList.tsx`, `frontend/src/components/DetailPanel.tsx`

## Bizonytalanságok

- Az ÖREB zónák kantononként eltérő elnevezési konvenciói (WFS WGS84 illesztés).
