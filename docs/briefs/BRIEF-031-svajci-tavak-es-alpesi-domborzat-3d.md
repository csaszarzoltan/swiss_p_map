# BRIEF-031: Svájci Tavak és Alpesi Domborzati Magasságok 3D-ben

**Státusz:** READY_FOR_SPEC  
**Kapcsolódó feature:** FEAT-031  
**Forrás:** a Swisstopo szövetségi vízrajzi adatai (swissTLM3D Gewässernetz), a 26 kanton átlagos tengerszint feletti magasságadatai (DHM25) és a Three.js 3D térképi megjelenítő alapján

## Probléma

A jelenlegi 3D térkép Svájcot teljesen sík felületű kantonokból állítja össze, a híres svájci tavak (Genfi-tó, Zürichi-tó, Vierwaldstättersee, Boden-tó, Neuchâteli-tó, Lago Maggiore, Luganói-tó) pedig nincsenek feltüntetve, vagy a kantonok határai között üres hézagként jelennek meg. A felhasználó így nem kapja meg a jellegzetes svájci alpesi és tóvidéki tájékozódási élményt.

## Célcsoport és kontextus

Minden látogató, ingatlanvásárló és elemző, aki a természetes svájci környezetben (tóparti fekvés, hegyvidéki magasság) szeretné elhelyezni a településeket és építkezéseket.

## Kívánt eredmény

Egy autentikus, vizuálisan magával ragadó 3D térkép:
1. **Svájci Tavak:** A 10 legnagyobb svájci tó pontos 3D geometriája csillogó, áttetsző ciánkék anyaggal (Three.js MeshPhysicalMaterial / Water shader), finom hullámzási csillogással.
2. **Alpesi Domborzati Extrudálás:** A kantonok 3D magassága (Z-tengely) arányos a kanton átlagos domborzati magasságával (pl. Valais 1892m, Graubünden 1800m, Uri 1600m magasabban emelkedik ki, míg Basel 280m és Genf 375m alacsonyabb platót képez).
3. **Interaktivitás:** A tavak fölé húzva az egeret megjelenik a tó neve és területe (pl. *"Zürichsee · 88.66 km²"*).

## Jelenlegi / Tervezett funkciókat lefedő felhasználói történetek

- **US-031-01:** Látogatóként a 3D térképet forgatva látni szeretném a svájci nagy tavak valósághű, csillogó kék körvonalait a kantonok között.
- **US-031-02:** Felhasználóként oldalnézetből döntve a térképet érzékelni szeretném a svájci Alpok és a síkvidéki kantonok közötti magassági lépcsőket.
- **US-031-03:** Felhasználóként egy tóra kattintva látni szeretném a tó körüli kiemelt part menti településeket és építkezéseket.
- **US-031-04:** Gyengébb hardverrel (mobil / integrált GPU) rendelkező felhasználóként szeretném, ha a tó-effektusok automatikusan egyszerűsített shaderre váltanának a stabil 60 FPS sebesség fenntartásához.

## Scope

- A 10 legnagyobb svájci tó 2D poligonjainak és 3D hálójának elkészítése (`swissLakes.ts`).
- Magassági skálázás (Elevation Z-offset) a 26 kantonális mesh-re (`swissCantons.ts`).
- Raycaster támogatás a tavak azonosításához lebegő tooltippel.
- Teljesítmény-érzékeny shader egyszerűsítés alacsony képkockasebesség esetén.

## Non-scope

- Több gigabájtos, ultra-részletes 1 méteres lézeres magasságmodell (DEM) betöltése a böngészőbe (marad a sematikus, stílusos alpesi blokkmodell).
- Hajózási útvonalak és vízmélység-térkép.

## Érintett rendszerek

- `frontend/src/app/Map3D.tsx`, `frontend/src/app/swissCantons.ts`, `frontend/src/app/swissLakes.ts` [ÚJ]

## Bizonytalanságok

- A határmenti tavak (pl. Genfi-tó francia része, Boden-tó német/osztrák része) határvonal-kezelése (a teljes tó geometriája vagy a svájci vízfelület jelenjen-e meg).
