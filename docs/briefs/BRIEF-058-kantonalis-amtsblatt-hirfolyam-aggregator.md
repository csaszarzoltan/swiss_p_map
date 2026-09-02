# BRIEF-058: Kantonális E-Amtsblatt és Hivatalos Közlöny Hírfolyam Aggregátor

**Státusz:** READY_FOR_SPEC  
**Kapcsolódó feature:** FEAT-058  
**Forrás:** 2. Opció (Valódi Élő Svájci OGD & Külső API Integrációk), kantonális E-Amtsblatt portálok (pl. amtsdruckschriften.ch, shab.ch, zh.ch/amtsblatt) és a `SPEC-047` specifikáció alapján

## Probléma

A kantonok és önkormányzatok hivatalos döntései, az új rendeletek, az útlezárások, a környezetvédelmi határozatok és a közmeghallgatások a kantonális hivatalos közlönyökben (*Amtsblatt*) jelennek meg. Ezek az adatok jelenleg széttagoltan, 26 különböző formátumban érhetők el, így a polgárok szinte soha nem értesülnek róluk időben.

## Célcsoport és kontextus

Minden kantonális és helyi lakos, jogász, ingatlantulajdonos és helyi vállalkozó.

## Kívánt eredmény

Egy kantonális közlöny- és hírfolyam-aggregátor pipeline:
1. **Közlöny RSS & API Ingestion Pipeline:**
   - Kantonális E-Amtsblatt és önkormányzati sajtóközlemények automatikus periodikus beolvasása (napi 1-szer, éjszaka).
2. **Strukturált Kategorizálás és Kivonatolás:**
   - A közlönybejegyzések automatikus besorolása a 3 szintes modell szerint (*Mi történt / Miért fontos / Mi következik*).
   - Témacímkék hozzárendelése: Közlekedés (*Verkehr*), Építésügy (*Bauwesen*), Pénzügy (*Finanzen*), Környezetvédelem (*Umwelt*), Igazgatás (*Verwaltung*).
3. **Földrajzi Térbeli Címkézés:**
   - Helynevek, címek és parcellaszámok felismerése és összekötése a Swiss P Map belső helyfeloldójával (`PlaceService`).
4. **Hiteles Forráslink és Eredetiség:**
   - Minden tétel közvetlen permalinket kap a kantonális közlöny hivatalos bejegyzésére.

## Jelenlegi / Tervezett funkciókat lefedő felhasználói történetek

- **US-058-01:** Helyi lakosként szeretném látni a lakókörzetemet érintő legfrissebb hivatalos kantonális közlönybejegyzéseket közérthetően összefoglalva.
- **US-058-02:** Felhasználóként egy tervezett helyi útlezárásról vagy felújításról szeretnék hetekkel előre értesülni.
- **US-058-03:** Felhasználóként szeretném egyetlen kattintással megnyitni a kanton hivatalos PDF/HTML közlönyét a forrás hitelességének ellenőrzésére.

## Scope

- `src/services/connectors/amtsblatt_news_pipeline.py` szolgáltatás.
- RSS/Atom és JSON formátumú kantonális közlöny parser (ZH, BE, BS, LU, SG, ZG kantonok prioritásával).
- `local_news_service.py` összekötése az aggregált híradatbázissal.

## Non-scope

- Zárt, fizetős prémium médiaarchívumok jogtalan scrapingje.

## Érintett rendszerek

- `src/services/local_news_service.py`, `src/services/connectors/`, `src/db/planning_repo.py`
