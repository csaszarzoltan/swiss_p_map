# BRIEF-034: Svájci Lakásingatlan-Ártrendek és Piaci Index

**Státusz:** READY_FOR_SPEC  
**Kapcsolódó feature:** FEAT-034  
**Forrás:** BFS/FSO lakóingatlanár-index (IMPI), kantonális statisztikai hivatalok és piaci igény

## Probléma

A körzeti profil sok életminőségi és tervezési adatot mutat, de nem teszi láthatóvá, hogyan változtak a lakóingatlanárak, így a felhasználó nem tudja a helyszínt piaci kontextusban értékelni.

## Célcsoport és kontextus

Lakásvásárlók, eladók, banki elemzők és befektetők, amikor településeket vagy régiótípusokat hasonlítanak össze.

## Kívánt eredmény

Negyedéves, forrásolt árszint- és trendkártya, idősoros diagram és térképi változási réteg jelenik meg, amely külön kezeli a családi házakat és a társasházi lakásokat.

## Jelenlegi / Tervezett funkciókat lefedő felhasználói történetek

- **US-034-01:** Felhasználóként szeretném egy körzetnél látni a legfrissebb hivatalos árindexet és éves változást, hogy értsem a piaci irányt.
- **US-034-02:** Lakáskeresőként szeretném összehasonlítani két régió vagy településtípus trendjét, hogy megalapozottabban válasszak.
- **US-034-03:** Felhasználóként szeretném, hogy túl kevés helyi tranzakció esetén a rendszer magasabb aggregációs szintre váltson és ezt jelezze, hogy ne kapjak hamis pontosságot.
- **US-034-04:** Képernyőolvasós vagy billentyűzetes felhasználóként szeretném a diagram értékeit táblázatos alternatívában is elérni, hogy a trend vizuális grafikon nélkül is érthető legyen.

## Scope

- BFS IMPI negyedéves idősor, objektumtípus és régió-/községtípus szerinti bontás.
- Trendkártya, idősoros diagram, térképi színskála, forrás és frissesség.
- Összehasonlítási és exportkapcsolat a BRIEF-028 és BRIEF-020 képességekkel.

## Non-scope

- Egyedi ingatlan értékbecslése, hirdetési ár becslése vagy hiteltanácsadás.

## Érintett rendszerek

- tervezett src/services/property_market_service.py
- tervezett árindex modellek és cache-tábla
- frontend trend chart és tematikus réteg
- BFS PXWeb/OGD vagy publikált IMPI adatok

## Bizonytalanságok

- Az IMPI hivatalos felbontása nem feltétlenül ér el PLZ-szintig; a nominális és reálváltozás értelmezését, valamint a ritka tranzakciók adatvédelmét külön SPEC-ben kell rögzíteni.
