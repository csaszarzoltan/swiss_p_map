# BRIEF-045: Resident-First Helyi Információs Központ és Életviteli Portál Architektúra

**Státusz:** READY_FOR_SPEC  
**Kapcsolódó feature:** FEAT-045  
**Forrás:** OpenBorough civic information platform architektúra, a 2026-09-02-i termékstratégiai újratervezés és a `docs/product/RESIDENT-FIRST-INFORMATION-ARCHITECTURE.md` dokumentum alapján

## Probléma

A korábbi felület vizuálisan azt sugallta, hogy maga a 3D térkép a termék, és a teljes képernyőt elfoglalta. A svájci lakosok és beköltözők számára azonban az elsődleges érték az, hogy gyorsan, közérthetően és strukturáltan átlássák: *"Mi fontos ma az én településemen?"*. A térképnek ennek megfelelően elemzőeszközként kell szolgálnia, nem pedig egyedüli fókuszként.

## Célcsoport és kontextus

Minden svájci állampolgár, helyi lakos, beköltöző és bérlő, aki a településén (PLZ) történő politikai, környezeti, gazdasági és építési változásokról szeretne egyetlen tiszta felületen tájékozódni.

## Kívánt eredmény

Egy modern, "Resident-First" információs portál kezdőlap:
1. **Életviteli Központ (Local Information Hub):** A kereső alatt azonnal megjelenő 6+1 témakártya (Szavazások, Környezet, Időjárás, Lakhatás & Költségek, Mobilitás, Építkezések, Önkormányzat).
2. **Összecsukható Térképi Elemzőmodul (`▶ Räumliche Analyse und Karte`):** A 3D Three.js térkép alapértelmezetten diszkréten, de bármikor egy kattintással lenyithatóan jelenik meg.
3. **„Auf Karte” Közvetlen Ugrás:** Minden témakártyáról egyetlen gombnyomással megnyitható a megfelelő térképréteg és szűrő.
4. **Helyi Napi Briefing API:** `GET /api/v1/local/briefing?postcode={postcode}` végpont által szolgáltatott, forrásellenőrzött helyi összefoglaló.

## Jelenlegi / Tervezett funkciókat lefedő felhasználói történetek

- **US-045-01:** Helyi lakosként a településemre rákeresve azonnal a napi helyi összefoglalót és a 6 fő témakártyát szeretném látni ahelyett, hogy egy üres vagy domináns térkép töltene be.
- **US-045-02:** Felhasználóként szeretném, ha a 3D térképet igény szerint, egyetlen kattintással lenyithatnám mélyebb térbeli elemzéshez.
- **US-045-03:** Felhasználóként egy témakártyán (pl. Adóverseny vagy Építkezések) az "Auf Karte" gombra kattintva azonnal a releváns hőtérképhez vagy marker-csoporthoz szeretnék jutni.
- **US-045-04:** Felhasználóként szeretném látni a kártyák prioritását (urgent, important, normal) és a hivatalos forrásmegjelölést.

## Scope

- `frontend/src/components/LocalInformationHub.tsx` komponens integrációja a kezdőlapra.
- `src/services/local_information_service.py` szolgáltatás és `GET /api/v1/local/briefing` végpont.
- Összecsukható térképes konténer és állapotvezérelt rétegváltás.

## Non-scope

- Közösségi média kommentfal és felhasználói fórum üzemeltetése.

## Érintett rendszerek

- `frontend/src/app/[locale]/page.tsx`, `frontend/src/components/LocalInformationHub.tsx`, `src/services/local_information_service.py`, `src/main.py`

## Bizonytalanságok

- Nagyon kis lélekszámú kistelepüléseknél a kantonális adatok aggregációjának mélysége (autonóm kantonális fallback biztosított).
