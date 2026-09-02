# BRIEF-057: Élő SBB OpenData / Transport API Menetrendi Konnektor

**Státusz:** READY_FOR_SPEC  
**Kapcsolódó feature:** FEAT-057  
**Forrás:** 2. Opció (Valódi Élő Svájci OGD & Külső API Integrációk), SBB Open Data / OpenData.ch Swiss Transport API és a `SPEC-033` specifikáció alapján

## Probléma

A tömegközlekedési elérhetőség Svájcban a lakóhelyválasztás és a mindennapi élet egyik legfontosabb tényezője. A statikus menetrendi modellek helyett a lakosoknak valós idejű SBB/ZVV/TPG/TILO járatinformációkra, peroninformációkra és valós menetidőkre van szükségük a legfontosabb gazdasági központok felé.

## Célcsoport és kontextus

Minden svájci ingázó, vasúton közlekedő lakos és az ingatlanok közlekedési kapcsolatát elemző vásárló/bérlő.

## Kívánt eredmény

Egy élő SBB / Swiss Public Transport API konnektor:
1. **Élő Indulási Tábla (*Live Abfahrtstafel*):**
   - A kiválasztott településhez/címhez legközelebbi vasútállomás és buszmegálló következő 5 induló járata peronszámmal, célállomással és késési információval (+perc).
2. **Központi Csomóponti Menetidők (*Hub-Reisezeiten Live*):**
   - Pontos, valós idejű utazási idő a 4 svájci metropoliszba (Zürich HB, Bern, Basel SBB, Genève Cornavin) a következő leggyorsabb csatlakozással.
3. **Utolsó Esti Csatlakozás (*Letzter Heimweg*):**
   - Mikor indul az utolsó vonat/busz a nagyvárosból hazafelé (különösen fontos a vidéki és agglomerációs településeken élőknek).
4. **Hálózati Zavarinformációk (*SBB Betriebslage & Störungsmeldungen*):**
   - Érintett vasútvonalak karbantartási vagy havária miatti kiesései.

## Jelenlegi / Tervezett funkciókat lefedő felhasználói történetek

- **US-057-01:** Ingázóként a kezdőlapon szeretném látni a helyi vasútállomás következő járatait és az esetleges késéseket.
- **US-057-02:** Felhasználóként látni akarom, hogy pontosan mennyi idő alatt érek be a munkahelyemre a következő vonattal.
- **US-057-03:** Fiatal lakosként tudni akarom, hogy a legközelebbi nagyvárosból mikor indul az utolsó éjszakai vonat (SN) a településemre.

## Scope

- `src/services/connectors/sbb_transport_client.py` konnektor.
- OpenData.ch `transport.opendata.ch/v1/` és SBB API integráció.
- Caching és sebességoptimalizálás (30 mp TTL).

## Non-scope

- Közvetlen vonatjegy és SBB SwissPass bérletvásárlási tranzakciók lebonyolítása.

## Érintett rendszerek

- `src/services/transit_mobility_service.py`, `src/services/connectors/`, `frontend/src/components/ResidentCivicPanels.tsx`
