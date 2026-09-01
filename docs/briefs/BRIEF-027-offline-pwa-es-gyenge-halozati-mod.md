# BRIEF-027: Offline PWA és Gyenge Hálózati Mód

**Státusz:** READY_FOR_SPEC  
**Kapcsolódó feature:** FEAT-027  
**Forrás:** felhasználói igény és mobil terméklogika

## Probléma
A térképi alkalmazás külső OGD szolgáltatásokra támaszkodik; terepen vagy gyenge mobilhálózaton a felület részben vagy teljesen használhatatlanná válhat.

## Célcsoport és kontextus
Mobilos lakosok és szakemberek, akik helyszínen, változó hálózati minőség mellett nyitják meg a korábban vizsgált körzetet.

## Kívánt eredmény
Az alkalmazás telepíthető PWA-ként; a felhasználó látja az online/offline állapotot, és eléri a legutóbb megnyitott, időbélyeggel jelölt körzeti adatokat.

## Jelenlegi / Tervezett funkciókat lefedő felhasználói történetek
- **US-027-01:** Mobilfelhasználóként szeretném telepíteni az alkalmazást a kezdőképernyőre.
- **US-027-02:** Felhasználóként szeretném offline megnyitni a legutóbb használt körzet alapadatait.
- **US-027-03:** Felhasználóként szeretném látni, mely adatok cache-ből származnak és mikor frissültek.
- **US-027-04:** Felhasználóként szeretném, hogy online állapot visszatérésekor a frissítés biztonságosan megtörténjen, konfliktus vagy üres nézet nélkül.

## Scope
- Web app manifest, service worker, app shell és korlátozott adatcache.
- Offline állapot, frissességi jelzés és kontrollált újraszinkronizálás.

## Non-scope
- Teljes Svájc térképcsempéinek vagy 22k rekordjának korlátlan offline letöltése.

## Érintett rendszerek
- frontend PWA konfiguráció
- frontend API cache réteg
- backend cache headers és adatverziók

## Bizonytalanságok
- Külső térképi licencek offline cache feltételei, eszköztárhely-korlátok és érzékeny mentett állapot kezelése.
