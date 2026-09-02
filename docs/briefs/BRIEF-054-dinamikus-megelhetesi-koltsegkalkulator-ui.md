# BRIEF-054: Dinamikus Svájci Megélhetési és Lakhatási Költségkalkulátor UI

**Státusz:** READY_FOR_SPEC  
**Kapcsolódó feature:** FEAT-054  
**Forrás:** 1. Opció (Civic Panelek Prémium UI Redesignja), OpenBorough Affordability UI és a `SPEC-049` specifikáció alapján

## Probléma

A svájci lakhatási és megélhetési költségek kiszámítása rendkívül komplex, mert a lakbér, az adókulcs (*Steuerfuss*), a kötelező betegbiztosítás (*Krankenkasse*) és a közlekedés költsége kantononként és településenként drasztikusan eltér. Egy statikus táblázat helyett egy interaktív, csúszkákkal állítható vizuális kalkulátorra van szükség.

## Célcsoport és kontextus

Költözést tervező svájci és külföldi munkavállalók, családok, egyedülállók és ingatlanvásárlók.

## Kívánt eredmény

Egy csúszkás, valós idejű költségkalkulátor felület:
1. **Interaktív Bemeneti Csúszkák (*Eingabe-Slider*):**
   - Bruttó éves jövedelem (pl. CHF 60'000 – CHF 300'000).
   - Háztartás típusa (Egyedülálló, Pár, 1–3 gyermekes család).
   - Lakásméret / Szobaszám (1.5 – 5.5 szoba) vagy vétel / bérlet váltó.
2. **Dinamikus Költségbontási Kördiagram & Oszlopdiagram (*Kosten-Aufschlüsselung*):**
   - Lakbér / Törlesztőrészlet (CHF/hó).
   - Kantonális & Települési Jövedelemadó (CHF/hó, pontos Steuerfuss alapján).
   - Krankenkassen alapbiztosítás (BAG díjrégió szerint).
   - Helyi tömegközlekedési bérlet (ZVV/SBB GA/Halbtax).
3. **Települési Összehasonlító Mérleg (*Vergleichs-Simulator*):**
   - Két település (pl. Zürich 8004 vs. Zug 6300 vagy Bern 3011) közvetlen összevetése: kimutatja a havi nettó megtakarítási különbséget.
4. **Kötelező Pénzügyi Felelősségkizárás (*Disclaimer*):**
   - Jól látható jelölés, hogy a számítás tájékoztató becslés (`modeled_estimate`), nem minősül hivatalos adótanácsadásnak.

## Jelenlegi / Tervezett funkciókat lefedő felhasználói történetek

- **US-054-01:** Felhasználóként a jövedelem-csúszkát mozgatva valós időben szeretném látni a várható havi adómat és megélhetési kiadásaimat az adott településen.
- **US-054-02:** Felhasználóként látni szeretném a lakbér és az adókulcs arányát egy elegáns vizuális kördiagramon.
- **US-054-03:** Családként össze szeretném hasonlítani a jelenlegi lakóhelyem és egy kiszemelt új település valós nettó költségkülönbségét.

## Scope

- `frontend/src/components/civic/CostOfLivingCalculator.tsx` komponens.
- Csúszkás vezérlők, SVG/Canvas diagramok és valós idejű API lekérdezés (`/api/v1/costs/assessment`).

## Non-scope

- Banki hitelbírálat vagy jelzáloghitel-szerződés közvetlen kötése.

## Érintett rendszerek

- `frontend/src/components/ResidentCivicPanels.tsx`, `src/services/cost_of_living_service.py`
