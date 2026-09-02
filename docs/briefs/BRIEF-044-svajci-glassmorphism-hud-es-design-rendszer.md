# BRIEF-044: Svájci Glassmorphism HUD és Vizuális Design Rendszer

**Státusz:** READY_FOR_SPEC  
**Kapcsolódó feature:** FEAT-044  
**Forrás:** a UI/UX Prémium Redesign Sprint, a Three.js 3D térképi HUD réteg, a Glassmorphism utility rendszer (`globals.css`) és a Swiss Typography statisztikai kártyák alapján

## Probléma

A térinformatikai és körzeti adatok korábban hagyományos, szürke, dobozos elrendezésben jelentek meg, amely összenyomta a 3D térképet és nem nyújtotta a svájci digitális termékekre jellemző letisztult, prémium ("Swiss Design") esztétikát és azonnali átláthatóságot.

## Célcsoport és kontextus

Minden látogató, döntéshozó és ingatlanelemző asztali gépen és mobilon, aki modern, tágas és elegáns felületen szeretné böngészni a svájci adatokat.

## Kívánt eredmény

Egy egységes lebegő üveg (Glassmorphism HUD) felhasználói felület:
1. **Lebegő Fejléc & Kereső:** Sötét kiber-üveg hatású, áttetsző panel (`backdrop-blur-xl bg-slate-950/80 border-b border-white/10`) lekerekített keresőmezővel és stílusos Quick-Pick gombokkal.
2. **Kapszula Téma-navigáció:** Lebegő, animált pill-tab sáv (`TopicSidebar.tsx`) színátmenetes aktív állapottal és számláló jelvényekkel.
3. **Svájci Statisztikai Kártyarács:** Nagy kontrasztú kulcsszámok (Steuerfuss %, dB(A), ÖV-Klasse, kWh/m²) és kiemelt AI Executive Summary kártya izzó kerettel.
4. **Csillogó 3D Vízfelületek:** A svájci tavak fényvisszaverő, áttetsző vízkék anyaga a Three.js térképen.

## Jelenlegi / Tervezett funkciókat lefedő felhasználói történetek

- **US-044-01:** Látogatóként a térképet nézve szeretném, hogy a vezérlők és fejlécek elegánsan a térkép felett lebegjenek, maximális teret engedve a 3D vizualizációnak.
- **US-044-02:** Felhasználóként szeretném a 4 fő körzeti mutatót (adó, zaj, tömegközlekedés, napenergia) nagyméretű, tiszta statisztikai kártyákon látni.
- **US-044-03:** Felhasználóként szeretném, ha a témák közötti váltás finom színátmenetes animációval és pill-tab állapotjelzővel történne.
- **US-044-04:** Mobilos látogatóként szeretném, ha a lebegő panelek és a témasáv reszponzívan, vízszintesen görgethetően és érintésbarát gombokkal működnének.

## Scope

- Glassmorphism stílusosztályok a `globals.css` fájlban (`.glass-panel`, `.glass-pill`, `.glow-cyan`, `.glow-amber`).
- Átdolgozott `page.tsx`, `TopicSidebar.tsx`, `SearchPanel.tsx`, `DetailPanel.tsx` és `TopicList.tsx` komponensek.
- 3D tavi felületek shader-anyaga a `Map3D.tsx`-ben.

## Non-scope

- 3D VR/AR szemüveges WebXR támogatás.

## Érintett rendszerek

- `frontend/src/app/globals.css`, `frontend/src/app/[locale]/page.tsx`, `frontend/src/components/TopicSidebar.tsx`, `frontend/src/components/DetailPanel.tsx`, `frontend/src/components/TopicList.tsx`, `frontend/src/app/Map3D.tsx`

## Bizonytalanságok

- Nagyon gyenge mobil hardvereken a `backdrop-blur` CSS szűrő hardveres gyorsítása (Tailwind fallback támogatott).
