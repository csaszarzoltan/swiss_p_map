# BRIEF-036: ISOS Műemlékvédelmi és Történeti Településréteg

**Státusz:** READY_FOR_SPEC  
**Kapcsolódó feature:** FEAT-036  
**Forrás:** BAK/FOC ISOS szövetségi inventár, Swisstopo FSDI geoszolgáltatások és kantonális műemléki nyilvántartások

## Probléma

A zónabesorolás önmagában nem mutatja meg, hogy egy épület vagy településrész országos jelentőségű történeti környezetben fekszik-e, ami az átalakítási lehetőségeket és a hely karakterét jelentősen befolyásolhatja.

## Célcsoport és kontextus

Tulajdonosok, építészek, ingatlanfejlesztők, örökségvédelmi szakemberek és kulturális érdeklődők felújítás vagy helyszínértékelés során.

## Kívánt eredmény

Kapcsolható ISOS-réteg, településkép-poligonok, védelmi célok, információs kártya, hivatalos PDF-link és világos jogi státusz jelenik meg.

## Jelenlegi / Tervezett funkciókat lefedő felhasználói történetek

- **US-036-01:** Tulajdonosként szeretném látni, hogy a vizsgált cím ISOS-érintett területen van-e, hogy időben bevonhassak szakértőt.
- **US-036-02:** Építészként szeretném megnyitni a kapcsolódó hivatalos ISOS leírást és védelmi célokat, hogy a koncepciót a környezethez igazítsam.
- **US-036-03:** Felhasználóként szeretném, hogy csak PDF-ben érvényes vagy még nem vektorizált felvétel esetén a rendszer ezt jelezze, és a PDF-re irányítson.
- **US-036-04:** Billentyűzetes és képernyőolvasós felhasználóként szeretném a térképi poligonok lényegét strukturált listában is elérni.

## Scope

- ISOS I és ISOS II rekordok megkülönböztetése.
- Vektoros területek, attribútumok, fényképekhez vagy hivatalos dokumentumhoz vezető linkek.
- Planning és Baugesuch detail panelben örökségvédelmi kontextusjelzés.

## Non-scope

- Automatikus műemlékvédelmi engedély, jogi megfelelőségi döntés vagy szerzői joggal védett teljes dokumentumok újraközlése.

## Érintett rendszerek

- tervezett src/services/heritage_service.py
- frontend heritage layer és detail card
- BAK ISOS WMS/WMTS/API
- kantonális inventárak későbbi adapterei

## Bizonytalanságok

- A BAK szerint a vektoros geoadat tájékoztató jellegű, míg a PDF lehet jogilag irányadó; az ISOS revízió fokozatos és a részletesség területenként eltér.
