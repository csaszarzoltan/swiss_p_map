# BRIEF-043: Épületenergetika, Felújítási Potenciál és Fűtéscsere

**Státusz:** READY_FOR_SPEC  
**Kapcsolódó feature:** FEAT-043  
**Forrás:** BFE/SFOE, GWR, kantonális energiakataszterek és Gebäudeprogramm tájékoztatók

## Probléma

A Sonnendach réteg csak a napenergia-potenciált mutatja; az épület kora, fűtési módja, becsült felújítási igénye, hőhálózati lehetősége és támogatási kontextusa nem áll össze egységes képpé.

## Célcsoport és kontextus

Tulajdonosok, társasházak, energetikai tanácsadók és vásárlók felújítás vagy fűtéscsere előkészítésekor.

## Kívánt eredmény

Épület- vagy körzetszintű energiahelyzet-kártya jelenik meg ismert GWR jellemzőkkel, helyi energiaforrásokkal, tájékoztató felújítási lépésekkel és hivatalos támogatási linkekkel.

## Jelenlegi / Tervezett funkciókat lefedő felhasználói történetek

- **US-043-01:** Tulajdonosként szeretném látni az épület ismert korát, fűtési energiahordozóját és napenergia-potenciálját, hogy azonosítsam a további energetikai vizsgálat témáit.
- **US-043-02:** Felhasználóként szeretném látni, van-e a közelben távhő, geotermikus korlátozás vagy kantonális energiatervezési információ.
- **US-043-03:** Felhasználóként szeretném, hogy hiányzó vagy becsült épületadat esetén a rendszer ezt jelezze, és ne számítson megtakarítást bizonyíték nélkül.
- **US-043-04:** Képernyőolvasós felhasználóként szeretném a prioritásokat, adatforrásokat és bizonytalanságokat lineáris, jól címkézett listában elérni.

## Scope

- GWR épületkor és elérhető fűtési adatok, BFE napenergia.
- Kantonális energiakataszter provider-adapterek: távhő, geotermikus alkalmasság vagy korlátozás.
- Tájékoztató felújítási checklist és hivatalos tanácsadási/támogatási linkek.

## Non-scope

- Automatikus GEAK/CECB tanúsítvány, kivitelezői ajánlat, támogatási jogosultság garantálása vagy személyre szabott beruházási megtérülés.

## Érintett rendszerek

- tervezett building_energy_service
- GWR és solar modellek bővítése
- frontend energy renovation panel
- BFE, kantonális energiakataszterek és támogatási portálok

## Bizonytalanságok

- Az épületszintű adatok hiányosak vagy hozzáférés-korlátosak lehetnek; a támogatások és műszaki korlátozások kantononként, időben változnak.
