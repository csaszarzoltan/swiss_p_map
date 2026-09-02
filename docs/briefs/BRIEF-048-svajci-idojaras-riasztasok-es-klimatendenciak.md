# BRIEF-048: Svájci Időjárás, Élő Riasztások és CH2025 Klímatendenciák Központ

**Státusz:** READY_FOR_SPEC  
**Kapcsolódó feature:** FEAT-048  
**Forrás:** MeteoSwiss OGD, BAFU/NABEL környezeti megfigyelések, WSL/SLF lavina- és hóadatok, CH2025 éghajlati szcenáriók és a 2026-09-02-i egyeztetés alapján

## Probléma

A legtöbb időjárási app egyetlen egyszerű hőmérséklet-grafikont mutat, miközben a svájci domborzat és alpesi sajátosságok miatt a lakosoknak kritikus szükségük van az élő viharriasztásokra, a hóhatárra, a nyári tavi fürdővíz-hőmérsékletekre, valamint a hosszabb távú hősziget- és klímatendenciákra. Fontos, hogy a napi előrejelzés és a hosszú távú klímamodell ne mosódjon össze egyetlen grafikonra.

## Célcsoport és kontextus

Svájcban élő családok, sportolók, hegyvidéki és tóparti lakosok, mezőgazdasági és építőipari szereplők.

## Kívánt eredmény

Egy integrált svájci meteorológiai és klímaközpont:
1. **Élő Időjárás és Riasztások (MeteoSwiss):**
   - Aktuális hőmérséklet, szél, páratartalom és 10 napos helyi előrejelzés.
   - Hivatalos 1–5-ös szintű riasztások (zivatar, jégeső, viharos szél, ónos eső, kánikula).
2. **Svájci Életviteli Mutatók:**
   - **Tavi & Folyami Vízhőmérsékletek:** Élő mérési adatok svájci tavakból és folyókból (pl. Zürichsee, Vierwaldstättersee, Limmat, Aare, Lac Léman).
   - **Téli Hegyi Mutatók:** Hóhatár (Schneefallgrenze), friss hóvastagság és WSL/SLF lavinaveszély-szintek.
3. **CH2025 Klímatendenciák & Hőszigetek:**
   - Trópusi éjszakák száma évente ($T_{\min} \ge 20^\circ\text{C}$).
   - Eltérés a hosszú távú éghajlati átlagtól ($+1.5^\circ\text{C}$ és $+3.0^\circ\text{C}$ szcenáriók).
   - **Tiszta módszertani szétválasztás:** Aktuális mérés (Official Measurement), 10 napos előrejelzés (Forecast Model) és klímaszimuláció (Climate Scenario).

## Jelenlegi / Tervezett funkciókat lefedő felhasználói történetek

- **US-048-01:** Helyi lakosként szeretném látni a MeteoSwiss hivatalos riasztási fokozatát és a várható heves esőzéseket a lakóhelyemen.
- **US-048-02:** Nyáron a tónál pihenve szeretném tudni a legközelebbi svájci tó pontos vízhőmérsékletét.
- **US-048-03:** Ingatlantulajdonosként szeretném megkülönböztetni a holnapi időjárást a 2030–2050-es CH2025 hősziget-kockázattól.

## Scope

- `src/services/weather_climate_service.py` szolgáltatás.
- `GET /api/v1/weather/current`, `GET /api/v1/weather/alerts`, `GET /api/v1/weather/water-temperatures` végpontok.
- UI kártyák és `Auf Karte` csapadék/hőtérkép rétegkapcsolat.

## Non-scope

- Saját meteorológiai numerikus futtatómodellek üzemeltetése (a rendszer a MeteoSwiss és BAFU adataira épít).

## Érintett rendszerek

- `src/services/microclimate_service.py`, `src/services/hazard_service.py`, `frontend/src/components/LocalInformationHub.tsx`
