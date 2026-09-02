# BRIEF-055: Élő MeteoSwiss OGD és Viharriasztási API Konnektor

**Státusz:** READY_FOR_SPEC  
**Kapcsolódó feature:** FEAT-055  
**Forrás:** 2. Opció (Valódi Élő Svájci OGD & Külső API Integrációk), MeteoSwiss Open Government Data (OGD) és a `SPEC-048` specifikáció alapján

## Probléma

A jelenlegi meteorológiai szolgáltatás robusztus beépített szimulációs modellel működik, de a felhasználók számára kiemelten fontos, hogy valós viharhelyzetben a Svájci Meteorológiai Szolgálat (MeteoSwiss) hivatalos, valós idejű mérési adatait és élő vészjelzéseit lássák.

## Célcsoport és kontextus

Minden svájci lakos, katasztrófavédelemben vagy kültéri munkában érintett polgár, akinek percrekész, hivatalos meteorológiai mérésekre van szüksége.

## Kívánt eredmény

Egy élő MeteoSwiss OGD adatcsatorna és konnektor:
1. **Élő Automata Mérőállomások Lekérdezése (MeteoSwiss SwissMetNet):**
   - Hivatalos állomások (pl. Zürich Fluntern, Bern Zollikofen, Basel Binningen, Genève Cointrin, Lugano) 10 percenként frissülő hőmérséklet, szélsebesség, páratartalom és csapadék adatfolyama.
2. **Hivatalos Veszélyriasztások (MeteoSwiss CAP / JSON Warnings API):**
   - Valós idejű vihar-, jég-, ónos eső-, havazás- és kánikula-riasztások kantonális és járási szinten (Warnregionen).
3. **BAFU Hidrológiai Élő Adatok (BAFU Hydrologische Messstationen):**
   - Svájci tavak és folyók élő vízhőmérséklete és vízhozama (m³/s).
4. **Hibakezelés és Intelligens Cache:**
   - Helyi Redis / In-Memory cache 5-10 perces TTL-lel a külső API tehermentesítésére.
   - Hálózati kimaradás esetén automatikus fallback a legutolsó érvényes mérésre `source: official_measurement (cached)` jelöléssel.

## Jelenlegi / Tervezett funkciókat lefedő felhasználói történetek

- **US-055-01:** Rendszerüzemeltetőként szeretném, hogy az időjárási modul a MeteoSwiss hivatalos OGD csatornájából olvassa a valós méréseket.
- **US-055-02:** Felhasználóként vihar idején percrekész, hivatalos MeteoSwiss figyelmeztetést akarok kapni az irányítószámomra.
- **US-055-03:** Felhasználóként a tónál a BAFU mérőállomásának hiteles, mai vízhőmérsékletét akarom látni.

## Scope

- `src/services/connectors/meteoswiss_client.py` és `bafu_hydro_client.py` kliensek.
- Hálózati aszinkron `httpx` integráció, időtúllépés-kezelés és JSON séma-transzformáció.
- `weather_climate_service.py` összekötése az élő klienssel.

## Non-scope

- Fizetős privát időjárási radar műholdképek dekódolása.

## Érintett rendszerek

- `src/services/weather_climate_service.py`, `src/services/connectors/`, `tests/unit/test_resident_first_services.py`
