# BRIEF-021: Tematikus Jelmagyarázat és Forráshivatkozás

**Státusz:** READY_FOR_SPEC  
**Kapcsolódó feature:** ADR-019  
**Forrás:** meglévő kód és ADR-019

## Probléma
A tematikus kantonszínek önmagukban nem mondják meg, milyen értéket vagy kategóriát jelentenek, mobilon pedig hover magyarázat sem áll rendelkezésre.

## Célcsoport és kontextus
Térképet böngésző lakosok, elemzők és akadálymentes megjelenítést igénylő felhasználók, amikor Politics, Solar vagy ÖREB témára váltanak.

## Kívánt eredmény
Aktív témánként azonnal frissülő, szöveges és színmintás jelmagyarázat jelenik meg hiteles forráslinkkel, mobilon és asztali nézetben is.

## Jelenlegi / Tervezett funkciókat lefedő felhasználói történetek
- **US-021-01:** Felhasználóként szeretném látni, mit jelentenek az aktuális témaréteg színei, hogy helyesen értelmezzem a térképet.
- **US-021-02:** Felhasználóként szeretném a jelmagyarázatból megnyitni a hivatalos adatforrást, hogy ellenőrizhessem az adat eredetét.
- **US-021-03:** Mobilfelhasználóként szeretném hover nélkül is elérni a jelmagyarázatot.
- **US-021-04:** Billentyűzetes és képernyőolvasós felhasználóként szeretném szemantikusan bejárni a jelmagyarázat elemeit.

## Scope
- Politics, Solar és ÖREB témák skálái és kategóriái.
- Aktív témához kötött megjelenítés, lokalizált címkék és külső forráslink.

## Non-scope
- Nyers WMS legendaképek letöltése és új backend végpont.

## Érintett rendszerek
- frontend/src/components/MapLegend.tsx
- frontend/src/app/[locale]/page.tsx
- frontend/messages/*.json

## Bizonytalanságok
- A BAFU és ÖREB forrásmegnevezés témánkénti pontosítása, valamint a színvak-biztos paletta végleges validálása.
