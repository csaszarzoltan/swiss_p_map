# BRIEF-008: Élő Kantonális Adókulcs Lekérdezés

**Státusz:** READY_FOR_SPEC  
**Kapcsolódó feature:** FEAT-008 (ADR-008)  
**Forrás:** a svájci kantonális adóhivatalok (pl. zh.ch Steueramt) nyilvános adatbázisa és a web scraper / API integráció alapján

## Probléma

A svájci önkormányzati adókulcsok (Gemeindesteuerfuss) évről évre változnak a helyi népszavazások és költségvetési döntések függvényében. A statikus adatok gyorsan elavulnak, ami téves pénzügyi döntésekhez vezethet az adózás terén.

## Célcsoport és kontextus

Munkavállalók, adótanácsadók és cégalapítók, akik a legalacsonyabb adóterhelésű svájci településeket keresik.

## Kívánt eredmény

Élő, naprakész adókulcs lekérdezés a kantonális forrásokból (pl. Zürich 119%, Uster 110%), pontos forrásmegjelöléssel (`steuerfuss_source: "zh-steueramt-html"`).

## Jelenlegi / Tervezett funkciókat lefedő felhasználói történetek

- **US-008-01:** Felhasználóként szeretném látni a település aktuális évi adókulcsát százalékban kifejezve.
- **US-008-02:** Felhasználóként szeretném látni, hogy az adat hivatalos élő forrásból származik-e.
- **US-008-03:** Rendszerként szeretném, ha a kantonális adóportál karbantartása esetén a rendszer a legutóbbi validált értékre állna vissza.

- **US-008-04:** Felhasználóként szeretném látni az adókulcs évét és frissességét, hogy elavult adattal ne hozzak pénzügyi döntést.

## Scope

- Aszinkron adókulcs lekérdező modul (`_fetch_zh_steuerfuss_live`).
- Forrás-metaadat visszaadása az API válaszban.
- Mockolt és élő egységtesztek (`test_place_zh_steuerfuss.py`).

## Non-scope

- Egyéni jövedelemadó-bevallás kalkulátor (csak a települési adókulcsot mutatjuk).

## Érintett rendszerek

- `src/services/place_service.py`, `src/models/place.py`, `src/main.py`

## Bizonytalanságok

- A nem-zürichi kantonok (pl. Schwyz, Zug, Bern) adóhivatali oldalainak formátum-különbségei.
