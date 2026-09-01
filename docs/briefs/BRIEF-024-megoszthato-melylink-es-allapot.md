# BRIEF-024: Megosztható Mélylink és Nyelvperzisztencia

**Státusz:** READY_FOR_SPEC  
**Kapcsolódó feature:** ADR-022  
**Forrás:** meglévő kód és ADR-022

## Probléma
A kiválasztott hely, téma, projekt és sugár újratöltéskor vagy linkküldéskor elveszhet, ezért az elemzési állapot nem reprodukálható.

## Célcsoport és kontextus
Felhasználók és szakmai együttműködők, akik egy konkrét térképi állapotot kollégával vagy családtaggal szeretnének megosztani.

## Kívánt eredmény
A URL tartalmazza a validált PLZ, topic, selected és radius állapotot; a másolt link ugyanazon a nyelven ugyanazt a nézetet állítja vissza.

## Jelenlegi / Tervezett funkciókat lefedő felhasználói történetek
- **US-024-01:** Felhasználóként szeretném egy gombbal a vágólapra másolni az aktuális nézet linkjét.
- **US-024-02:** Link címzettjeként szeretném ugyanazt a helyet, témát, kijelölést és sugarat látni.
- **US-024-03:** Felhasználóként szeretném, hogy a nyelvi útvonal megmaradjon a megosztott linkben.
- **US-024-04:** Felhasználóként szeretném, hogy hibás vagy manipulált query paraméterek biztonságos alapértékre essenek vissza.

## Scope
- State és URL kétirányú szinkronizálása.
- Copy link visszajelzés és query-validáció.

## Non-scope
- Szerveroldali rövidlink-szolgáltatás, felhasználói jogosultság és privát megosztás.

## Érintett rendszerek
- frontend/src/hooks/useShareableState.ts
- frontend/src/components/ShareButton.tsx
- frontend/src/app/[locale]/page.tsx

## Bizonytalanságok
- Clipboard API engedélyezése és fallback; történetkezelés back/forward navigációnál.
