# BRIEF-042: Szélessáv, Mobilhálózat és Digitális Elérhetőség

**Státusz:** READY_FOR_SPEC  
**Kapcsolódó feature:** FEAT-042  
**Forrás:** BAKOM/OFCOM szélessáv- és mobilhálózati adatok, kantonális infrastruktúra-portálok

## Probléma

A home office és digitális szolgáltatások alapvetőek, de a körzeti profil nem mutatja a vezetékes és mobilhálózati lefedettséget, technológiát vagy az adat bizonytalanságát.

## Célcsoport és kontextus

Távmunkában dolgozók, családok, vállalkozások és vidéki ingatlanok iránt érdeklődők helyszínválasztáskor.

## Kívánt eredmény

Cím vagy körzet körüli technológiasemleges digitális elérhetőségi kártya és térképréteg jelenik meg, szolgáltatófüggetlen forrás- és frissességi adatokkal.

## Jelenlegi / Tervezett funkciókat lefedő felhasználói történetek

- **US-042-01:** Távmunkásként szeretném látni, milyen vezetékes hozzáférési technológiák és névleges sebességkategóriák érhetők el a körzetben.
- **US-042-02:** Mobilfelhasználóként szeretném összevetni a hivatalos 4G/5G lefedettségi adatokat a domborzati kontextussal.
- **US-042-03:** Felhasználóként szeretném, hogy cím-pontosság hiányában a rendszer területi becslésként címkézze az adatot, és ne garantáljon tényleges szolgáltatást.
- **US-042-04:** Színlátási nehézséggel élő felhasználóként szeretném a lefedettségi kategóriákat szövegesen és mintázattal is megkülönböztetni.

## Scope

- BAKOM nyílt aggregált szélessáv- és mobil-lefedettségi adatok.
- Technológia, sebességkategória, felbontás, mérési vagy modellezési mód és frissesség.
- Tematikus overlay, összehasonlító kártya és export.

## Non-scope

- Egyedi szolgáltatói ajánlat, szerződéskötés, garantált beltéri jelerősség vagy valós sebességmérés.

## Érintett rendszerek

- tervezett connectivity_service
- frontend connectivity layer és compare metric
- BAKOM geoadat/API
- Swisstopo domborzati kontextus

## Bizonytalanságok

- Az adatok aggregáltak vagy szolgáltatói bejelentésen alapulhatnak; beltéri lefedettség és tényleges sebesség jelentősen eltérhet.
