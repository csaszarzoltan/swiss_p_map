# BRIEF-033: SBB Vasúti Mobilitási Főhálózat és Állomási Elérhetőség

**Státusz:** READY_FOR_SPEC  
**Kapcsolódó feature:** FEAT-033  
**Forrás:** a Svájci Szövetségi Közlekedési Hivatal (BAV - Bundesamt für Verkehr), a Svájci Szövetségi Vasutak (SBB CFF FFS OGD) nyílt menetrendi/hálózati API-ja és a 3D Three.js mobilitási vonalrajzoló motor alapján

## Probléma

A svájci életmód és ingatlanpiac egyik legfontosabb sarokköve a svájci óra pontosságú vasúti hálózat (Taktfahrplan) és az SBB közvetlen elérhetősége. Jelenleg a rendszerben a tömegközlekedés csak egyetlen statikus betűként jelenik meg ("ÖV-Klasse: Klasse A"), miközben nem láthatóak a főbb vasúti tengelyek (Zürich–Bern–Genf, Gotthard-bázisalagút, Lötschberg, Basel–Zürich), az állomási távolság és az utazási idők a kulcsközpontokhoz.

## Célcsoport és kontextus

Ingázók, környezettudatos lakosok, autómentes háztartások és ingatlanfejlesztők.

## Kívánt eredmény

Egy modern, interaktív vasúti mobilitási réteg:
1. **3D SBB Vasúti Hálózat:** A legfontosabb svájci InterCity (IC), InterRegio (IR) és alagúti tengelyek (Gotthard Base Tunnel 57km, Simplon, Lötschberg) finom, világító neonvonalakkal kirajzolva a 3D térképen.
2. **Közlekedési Csomópontok (Hubok):** A 20 legfontosabb svájci vasútállomás (Zürich HB, Bern, Basel SBB, Genève-Cornavin, Lausanne, Luzern, St. Gallen, Lugano) kiemelése pulzáló 3D markerekkel.
3. **Elérhetőségi / Ingázási Időprofil:** A kiválasztott település profiljában megjelenik a legközelebbi vasútállomás neve, távolsága (m), és a közvetlen menetidő a legközelebbi gazdasági központhoz (pl. *"Zürich HB: 14 perc S-Bahnnal"*).

## Jelenlegi / Tervezett funkciókat lefedő felhasználói történetek

- **US-033-01:** Felhasználóként a térképen bekapcsolva a "Mobilitás / SBB" réteget szeretném látni a svájci vasúti fővonalakat és a főbb alpesi bázisalagutakat.
- **US-033-02:** Felhasználóként egy településre kattintva szeretném látni a legközelebbi SBB vasútállomás nevét és gyalogos/tömegközlekedési távolságát.
- **US-033-03:** Felhasználóként látni szeretném az ingázási menetidőt Zürich, Bern vagy Genf központjába (pl. Uster -> Zürich HB 14 perc).
- **US-033-04:** Rendszerként szeretném, hogy az SBB hálózati adatok könnyű, vektoros polivonal formátumban (`swissRailways.ts`) töltsenek be a Three.js térképre, anélkül, hogy lassítanák a forgatást.

## Scope

- A svájci vasúti fővonalak és alagutak 3D vektoros polivonalai (`swissRailways.ts`).
- Főbb SBB állomások koordináta- és adatbázisa.
- Állomási távolság és utazási idő számító metódus a `PlaceService` modulban.
- Mobilitási kártya kibővítése a `DetailPanel.tsx` komponensben.

## Non-scope

- Valós idejű élő vonatkésés-követés másodpercre lebontva (nem utazástervező app, hanem ingatlan/körzeti mobilitási elemző).

## Érintett rendszerek

- `src/services/place_service.py`, `src/models/place.py`, `frontend/src/app/Map3D.tsx`, `frontend/src/app/swissRailways.ts` [ÚJ], `frontend/src/components/DetailPanel.tsx`

## Bizonytalanságok

- Részletes átszállási hálózatok (postabusz, helyi villamos/troli) integrálása kantonális szinten (első fázisban SBB vasúti gerinchálózat).
