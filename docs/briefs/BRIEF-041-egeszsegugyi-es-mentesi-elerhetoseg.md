# BRIEF-041: Egészségügyi és Mentési Elérhetőség

**Státusz:** READY_FOR_SPEC  
**Kapcsolódó feature:** FEAT-041  
**Forrás:** BFS/FSO egészségügyi statisztikák, BAG/FOPH intézményi adatok, kantonális egészségügyi és mentési portálok

## Probléma

A körzeti döntéstámogatás nem mutatja, milyen gyorsan érhető el alapellátás, gyógyszertár, sürgősségi osztály vagy kórház, ami családoknak és idősebb felhasználóknak fontos helyszínválasztási tényező.

## Célcsoport és kontextus

Családok, idősek, krónikus betegséggel élők, költözők és településtervezők, amikor a szolgáltatási elérhetőséget értékelik.

## Kívánt eredmény

Forrásolt egészségügyi intézményi réteg, nyitvatartási és elérhetőségi metaadat, valamint becsült utazási idő jelenik meg, világosan elválasztva a sürgősségi döntéstől.

## Jelenlegi / Tervezett funkciókat lefedő felhasználói történetek

- **US-041-01:** Lakóként szeretném látni a legközelebbi gyógyszertárat, háziorvosi vagy ügyeleti pontot és kórházat, hogy felmérjem az ellátási hozzáférést.
- **US-041-02:** Költözőként szeretném összehasonlítani több körzet tipikus tömegközlekedési és közúti elérési idejét a legközelebbi kórházig.
- **US-041-03:** Felhasználóként szeretném, hogy hiányzó vagy elavult nyitvatartás esetén a rendszer a hivatalos intézményi oldalra irányítson, és ne állítsa, hogy egy szolgáltatás nyitva van.
- **US-041-04:** Billentyűzetes és képernyőolvasós felhasználóként szeretném az intézményeket típus, távolság és akadálymentességi adat szerint szűrni.

## Scope

- Nyilvános intézményi pontok, típus, hivatalos link és ahol elérhető nyitvatartás.
- Távolság és normál közlekedési elérési idő, adatfrissesség.
- Akadálymentességi metaadat, ha hivatalosan rendelkezésre áll.

## Non-scope

- Segélyhívás, diagnózis, valós idejű mentőirányítás vagy garantált sürgősségi menetidő.

## Érintett rendszerek

- tervezett healthcare_access_service
- frontend service-access layer
- BAG/BFS és kantonális intézményi források
- SBB/öV és közúti hálózati routing

## Bizonytalanságok

- Nincs egységes, teljes országos valós idejű nyitvatartási és akadálymentességi adat; az útvonalidő nem használható vészhelyzeti döntésre.
