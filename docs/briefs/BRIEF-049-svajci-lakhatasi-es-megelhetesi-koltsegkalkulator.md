# BRIEF-049: Svájci Lakhatási és Megélhetési Költségkalkulátor

**Státusz:** READY_FOR_SPEC  
**Kapcsolódó feature:** FEAT-049  
**Forrás:** OpenBorough Affordability & Budget modul, a svájci szövetségi adórendszer (ESTV), a BFS IMPI ingatlanáradatbázis és a 2026-09-02-i egyeztetés alapján

## Probléma

A költözni vágyó vagy új otthont kereső svájci lakosok jelenleg 5–6 különböző portálról kénytelenek összevadászni a költségeket: külön nézik az ingatlanárat, a kantonális adókulcsot (*Steuerfuss*), a kötelező betegbiztosítási régiót (*Krankenkassen-Prämienregion*), az óvodai díjakat és az ingázási költségeket. Emiatt nincs egyetlen átfogó válasz a legalapvetőbb kérdésre: *"Mennyibe kerül itt élni?"*.

## Célcsoport és kontextus

Családok, pályakezdők, Svájcba költöző szakemberek és ingatlanbefektetők, akik reális, holisztikus képet keresnek egy adott település havi és éves megélhetési költségeiről.

## Kívánt eredmény

Egy integrált **„Mennyibe kerül itt élni?” (*Wohn- & Lebenskosten Hub*)** elemzőközpont:
1. **Lakhatási Árak és Bérleti Díjak (BFS IMPI):**
   - Átlagos CHF/m² vételár családi házra és társasházi lakásra.
   - Tipikus bérleti díjak szobaszám szerint és üres lakások aránya (*Leerwohnungsziffer*).
2. **Kantonális és Települési Adóhatás (ESTV):**
   - Települési adómérték (*Steuerfuss %*) és kantonális rangsor.
   - Adómegtakarítási szimuláció a szomszédos kantonokhoz képest (pl. ZH vs. SZ/ZG).
3. **Rejtett Helyi Költségtényezők:**
   - Betegbiztosítási díjrégió (BAG Prämienregion 1/2/3).
   - Óvodai és bölcsődei költségszintek (Kita-Kosten).
   - Épületenergetikai felújítási igény és távhő/hőszivattyú üzemeltetési költségvonzat.
   - SBB ingázási és tömegközlekedési költségek (GA / ZVV zónák).

## Jelenlegi / Tervezett funkciókat lefedő felhasználói történetek

- **US-049-01:** Felhasználóként egy településre rákeresve szeretném látni a becsült havi összköltséget (bérlet/hitel + adó + betegbiztosítás + közlekedés).
- **US-049-02:** Felhasználóként össze szeretném hasonlítani 2 település (pl. Zürich 8004 vs. Zug 6300) nettó megélhetési különbségét.
- **US-049-03:** Családként látni akarom, hogy a magasabb bérleti díj megtérül-e az alacsonyabb adóban és jobb iskolai elérhetőségben.

## Scope

- `src/services/cost_of_living_service.py` szolgáltatás.
- `GET /api/v1/costs/assessment?postcode={postcode}&income_chf={income}` végpont.
- Összehasonlító költségkártya a felületen.

## Non-scope

- Hivatalos adóbevallási szoftver helyettesítése vagy személyre szabott adótanácsadás.

## Érintett rendszerek

- `src/services/property_price_service.py`, `src/services/tax_service.py`, `src/services/district_comparison_service.py`, `frontend/src/components/LocalInformationHub.tsx`
