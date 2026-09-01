# BRIEF-037: Mikroklíma, Városi Hősziget és Klímajövő

**Státusz:** READY_FOR_SPEC  
**Kapcsolódó feature:** FEAT-037  
**Forrás:** MeteoSwiss városi hősziget adatok és CH2025 klímaszcenáriók, kantonális hőtérképek, Swisstopo felszínborítás

## Probléma

A jelenlegi körzeti profil nem mutatja a nyári éjszakai hőterhelést, a burkoltság és zöldfelület hatását, illetve a várható klímajelzőket, pedig ezek közvetlenül befolyásolják a komfortot és az egészséget.

## Célcsoport és kontextus

Városi lakosok, idősek, családok, településtervezők és ingatlanfejlesztők nyári hőség és hosszú távú helyszínválasztás idején.

## Kívánt eredmény

Interaktív hősziget- és klímaszcenárió nézet jelenik meg jelenlegi jelzőkkel, 1 km-es jövőbeli rácsokkal, zöldfelületi kontextussal és időhorizont-választóval.

## Jelenlegi / Tervezett funkciókat lefedő felhasználói történetek

- **US-037-01:** Lakáskeresőként szeretném látni a környék nyári hőterhelését és trópusi éjszakáit, hogy felmérjem a komfortot.
- **US-037-02:** Tervezőként szeretném összevetni a jelenlegi állapotot több CH2025 felmelegedési szinttel vagy időhorizonttal.
- **US-037-03:** Felhasználóként szeretném, hogy helyi mérés hiányában a rendszer a modellrács felbontását és bizonytalanságát jelezze, ne mutasson házszám-pontosságot.
- **US-037-04:** Kognitív vagy látási akadályozottsággal élő felhasználóként szeretném a színskála mellett egyszerű kategóriát és szöveges összefoglalót kapni.

## Scope

- MeteoSwiss CH2025 hő- és csapadékindikátorok.
- Kantonális városi klímatérképek, ahol nyíltan elérhetők.
- Időhorizont vagy globális felmelegedési szint választó, forrás és bizonytalanság.
- Zöldfelület, burkoltság és éjszakai hőterhelés magyarázó kártya.

## Non-scope

- Valós idejű egyéni egészségügyi riasztás, orvosi tanácsadás vagy épületenergetikai szimuláció.

## Érintett rendszerek

- tervezett climate_service és raster/vector tile cache
- frontend climate timeline és Map3D overlay
- MeteoSwiss CH2025 adatok
- kantonális klíma geoportálok

## Bizonytalanságok

- A városi mikroklíma sok helyen nem egységes országos felbontású; scenario-adat nem előrejelzés, ezért a kommunikáció és bizonytalansági metaadat kritikus.
