# BRIEF-052: Svájci Időjárási, Riasztási és Tavi Vízhőmérsékleti Widget

**Státusz:** READY_FOR_SPEC  
**Kapcsolódó feature:** FEAT-052  
**Forrás:** 1. Opció (Civic Panelek Prémium UI Redesignja), MeteoSwiss OGD és a `SPEC-048` specifikáció alapján

## Probléma

A svájci időjárás a hegyvidéki és tavi mikroklímák miatt rendkívül gyorsan változik. A lakosoknak nem egy száraz JSON táblázatra van szükségük, hanem egy vizuálisan tetszetős, azonnal értelmezhető időjárási és vészhelyzeti widgetre, amely a veszélyfokozatokat, a heti trendet és a tavi fürdővíz-hőmérsékleteket is látványosan ábrázolja.

## Célcsoport és kontextus

Minden svájci lakos, sportoló, szabadtéri tevékenységet tervező család és ingázó.

## Kívánt eredmény

Egy integrált időjárási és riasztási vizuális widget:
1. **7 Napos Vizuális Előrejelzési Sáv (*Weather Forecast Bar*):**
   - Napi időjárási ikonok, minimum és maximum hőmérsékleti skála és csapadékvalószínűség (% és mm).
2. **Élő Viharriasztási Jelvények (*MeteoSwiss Alert Badges*):**
   - 1–5-ös szintű hivatalos színkódolt riasztási sáv (Sárga: mérsékelt, Narancs: jelentős, Piros: nagy, Sötétpiros: nagyon nagy veszély) lejárati idővel és érintett területtel.
3. **Tavi & Folyami Vízhőmérséklet Kártya (*Wassertemperatur-Kachel*):**
   - A legközelebbi svájci tó/folyó (pl. Zürichsee 22.4°C, Limmat 20.1°C, Aare 19.5°C) grafikus hőmérséklet-mutatója és fürdési alkalmassági minősítése.
4. **Téli / Alpesi Mód (*Winter-Modus*):**
   - Hóhatár (Schneefallgrenze méterben), friss hóvastagság (cm) és SLF lavinaveszély-fokozat (1–5).

## Jelenlegi / Tervezett funkciókat lefedő felhasználói történetek

- **US-052-01:** Lakosként a kezdőlapra nézve azonnal látni akarom, hogy van-e aktív MeteoSwiss viharjelzés a körzetemben.
- **US-052-02:** Nyáron látni szeretném a hozzám legközelebbi svájci tó pontos vízhőmérsékletét egy vonzó widgeten.
- **US-052-03:** Felhasználóként szeretném a következő 7 nap várható hőmérsékleti sávját egyetlen görgetés nélkül átlátni.

## Scope

- `frontend/src/components/civic/WeatherVisualWidget.tsx` komponens.
- Viharriasztás-sáv, tavi hőmérsékleti skála és MeteoSwiss SVG ikonkészlet.

## Non-scope

- Radar-animációs videófájlok generálása közvetlenül a kliensben.

## Érintett rendszerek

- `frontend/src/components/ResidentCivicPanels.tsx`, `src/services/weather_climate_service.py`
