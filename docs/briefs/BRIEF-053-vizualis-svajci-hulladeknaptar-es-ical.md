# BRIEF-053: Vizuális Svájci Hulladéknaptár és Háztartási Naptár-integráció

**Státusz:** READY_FOR_SPEC  
**Kapcsolódó feature:** FEAT-053  
**Forrás:** 1. Opció (Civic Panelek Prémium UI Redesignja), a svájci önkormányzati hulladékgazdálkodás és a `SPEC-050` specifikáció alapján

## Probléma

Svájcban a hulladékkezelési szabályok szigorúak és a szállítási napok frakciónként (papír, karton, zöldhulladék, szemét) eltérőek. A lakosok gyakran elmulasztják a kéthetente/havonta egyszeri karton- vagy papírszállítást, mert az önkormányzati nyomtatott vagy nehezen átlátható PDF naptárakat nem figyelik.

## Célcsoport és kontextus

Minden svájci háztartás, bérlő és ingatlantulajdonos, aki szeretné zökkenőmentesen és időben kezelni a hulladékszállítást.

## Kívánt eredmény

Egy modern, interaktív hulladéknaptár widget:
1. **Színes Frakció-Ikonok (*Abfall-Fraktionen*):**
   - 📦 **Karton** (Kék ikon, kötegelési szabályok emlékeztetővel).
   - 📰 **Papír** (Világoskék ikon).
   - 🍏 **Bio / Zöldhulladék / Komposzt** (Barna/Zöld ikon).
   - 🗑️ **Háztartási Szemét (*Züri-Sack / Gebührensack*)** (Sötétszürke ikon).
   - 🔋 **Sonderabfall / E-hulladék** (Narancssárga veszélyjelzés gyűjtőpont-címmel).
2. **Következő Szállítási Nap Visszaszámláló (*Countdown Card*):**
   - Kiemelt vizuális figyelmeztetés: pl. *„Karton: Holnap (csütörtök) reggel 07:00-ig kihelyezendő!”*.
3. **iCal / Google Naptár Export Gomb (*1-Klick Kalenderimport*):**
   - Egyetlen kattintással letölthető `.ics` naptárfájl vagy közvetlen naptár-előfizetési link (WebCal) a felhasználó telefonos naptárjához.
4. **Helyi Szemeteszsák-illeték és Hulladékudvar Info (*Entsorgungshof*):**
   - Helyi hivatalos szemeteszsák-árak és legközelebbi hulladékudvar nyitvatartása.

## Jelenlegi / Tervezett funkciókat lefedő felhasználói történetek

- **US-053-01:** Lakosként a felületen azonnal látni szeretném a következő 3 hulladékszállítási napot a frakciók színes ikonjaival.
- **US-053-02:** Felhasználóként egyetlen gombnyomással importálni akarom az összes idei szállítási időpontot a telefonom naptárába (`.ics` formátumban).
- **US-053-03:** Új lakóként látni akarom a legközelebbi üveg-, alumínium- és textil-gyűjtőkonténerek helyét.

## Scope

- `frontend/src/components/civic/WasteCalendarVisual.tsx` komponens.
- iCal generáló funkció a böngészőben és letöltési művelet.
- Heti/havi naptárnézet és frakciószűrők.

## Non-scope

- Fizikai hulladékszállítási megrendelések közvetlen diszpécseri kezelése.

## Érintett rendszerek

- `frontend/src/components/ResidentCivicPanels.tsx`, `src/services/municipal_service.py`
