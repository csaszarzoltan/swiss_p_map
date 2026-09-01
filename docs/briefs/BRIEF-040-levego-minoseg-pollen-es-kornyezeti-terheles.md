# BRIEF-040: Levegőminőség, Pollen és Környezeti Terhelés

**Státusz:** READY_FOR_SPEC  
**Kapcsolódó feature:** FEAT-040  
**Forrás:** BAFU/FOEN NABEL levegőminőség, MeteoSwiss pollenadatok és kantonális mérőhálózatok

## Probléma

A zajadat mellett más, egészséget és mindennapi komfortot befolyásoló környezeti terhelések, például finompor, nitrogén-dioxid, ózon és pollen nem láthatók egységes helyi nézetben.

## Célcsoport és kontextus

Allergiával élők, családok, idősek, sportolók és környezettudatos költözők napi tájékozódáskor vagy helyszín-összehasonlításkor.

## Kívánt eredmény

Időbélyegzett levegőminőségi és pollenpanel jelenik meg mérőállomás-távolsággal, trenddel, hivatalos kategóriával és adatforrással.

## Jelenlegi / Tervezett funkciókat lefedő felhasználói történetek

- **US-040-01:** Felhasználóként szeretném látni a legközelebbi hivatalos mérőállomás PM2.5, PM10, NO2 és ózon értékeit, hogy megértsem a környezeti helyzetet.
- **US-040-02:** Allergiával élőként szeretném kiválasztani a számomra releváns pollentípusokat és látni a térségi terhelést.
- **US-040-03:** Felhasználóként szeretném, hogy állomási kiesés vagy túl nagy távolság esetén a rendszer jelezze a bizonytalanságot, és ne jelenítsen meg helyi mérésként regionális adatot.
- **US-040-04:** Képernyőolvasós felhasználóként szeretném a színkódolt kategóriák nevét, értékét, mértékegységét és időbélyegét felolvastatható formában megkapni.

## Scope

- NABEL és kantonális állomások, mért komponensek és frissesség.
- MeteoSwiss pollenrégiók vagy állomási adatok, felhasználó által választott pollenek.
- Trendnézet és térképi overlay világos mérés/modell megkülönböztetéssel.

## Non-scope

- Orvosi diagnózis, személyre szabott kezelési ajánlás vagy garantált egészségügyi kockázatbecslés.

## Érintett rendszerek

- tervezett environmental_health_service
- frontend air/pollen cards és thematic layer
- BAFU NABEL, MeteoSwiss és kantonális API-k

## Bizonytalanságok

- A pollenadatok térbeli felbontása és licencelése, a mérőállomások reprezentativitása és az egészségügyi kommunikáció megfogalmazása külön validációt igényel.
