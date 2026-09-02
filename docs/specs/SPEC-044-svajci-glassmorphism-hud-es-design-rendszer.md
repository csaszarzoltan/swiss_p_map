---
id: FEAT-044
title: Svájci Glassmorphism HUD és Vizuális Design Rendszer
status: SPEC_READY
version: 1
risk: low
owner: product-owner
approvedBy: system-architect
approvedAt: 2026-09-02T09:00:00Z
baseCommit: HEAD
brief: BRIEF-044
---

# FEAT-044: Svájci Glassmorphism HUD és Vizuális Design Rendszer

## 1. Cél és felhasználói eredmény

A felhasználó egy tágas, lebegő üveghatású (Glassmorphism HUD) felhasználói felületen böngészheti Svájc 3D térképét és adatait. A kulcsfontosságú mutatók (Steuerfuss, zaj, tömegközlekedés, napenergia, építkezések) nagyméretű, elegáns statisztikai kártyákon, azonnal átlátható tipográfiai hierarchiával jelennek meg.

## 2. Kontextus és források

- Kapcsolódó brief: `BRIEF-044` (`docs/briefs/BRIEF-044-svajci-glassmorphism-hud-es-design-rendszer.md`)
- Kapcsolódó ADR: `ADR-010`, `ADR-019`
- Kapcsolódó domain-invariánsok: `INV-DATA-001` forráshűség, `INV-TRACE-001` nyomkövethetőség, `INV-A11Y-001` akadálymentes kontraszt
- Implementációs bizonyíték: `frontend/src/app/globals.css`, `frontend/src/app/[locale]/page.tsx`, `frontend/src/components/DetailPanel.tsx`, `frontend/src/components/TopicSidebar.tsx`, `frontend/src/app/Map3D.tsx`

## 3. Scope

### Benne van
- Lebegő üveghatású fejléc, keresősáv és kapszula témasáv (`TopicSidebar.tsx`).
- 4 fős svájci statisztikai kártyarács a `DetailPanel.tsx`-ben és kiemelt AI Executive Summary blokk.
- Csillogó, áttetsző 3D tavi anyagok a `Map3D.tsx`-ben.
- Reszponzív, vízszintesen görgethető mobilos témasáv.

### Nincs benne
- Teljes egyedi CSS keretrendszer írása a Tailwind CSS helyett.
- 3D WebXR virtuális valóság eszközkezelés.

## 4. Szereplők és előfeltételek

- ACT-001: Látogató / Elemző asztali gépen vagy mobil böngészőben.
- PRE-001: A böngésző támogatja a CSS backdrop-filter és WebGL 3D renderelést.
- PRE-002: Térképi adatok és kantonális poligonok betöltődtek.

## 5. Funkcionális követelmények

- REQ-001 [MUST]: A rendszer a fejlécet és a témasávot lebegő üveghatású (Glassmorphism) stílussal jeleníti meg a 3D térképi canvas felett.
- REQ-002 [MUST]: Az áttekintő nézetben 4 kiemelt statisztikai kártya jeleníti meg a Steuerfusst, a zajszintet, az ÖV-osztályt és a napenergia-potenciált.
- REQ-003 [MUST]: Az AI Executive Summary kártya kiemelt, diszkrét izzó szegéllyel és ikonnal jelenik meg.
- REQ-004 [MUST]: A témaváltó fülek (pill-tabs) aktív állapotban színátmenetes kiemelést (`from-sky-500 to-blue-600`) és számláló jelvényt kapnak.
- REQ-005 [MUST NOT]: A lebegő panelek és kártyák nem takarhatják ki a térkép vezérlőit, és nem tehetik olvashatatlanná a szövegeket (megfelelő sötét elmosott háttér kötelező).
- REQ-006 [ALWAYS]: Minden interaktív gomb és kártya rendelkezik fókusz- és hover-visszajelzéssel.
- REQ-007 [CONCURRENCY]: Témaváltás és keresés közben a felület reszponzív marad, a 3D canvas 60 FPS sebességgel renderel.

## 6. Nem funkcionális követelmények

- NFR-001 [PERFORMANCE]: A felületi CSS stílusok és glassmorphism szűrők nem csökkenthetik a Three.js canvas képkockasebességét (cél: 60 FPS).
- NFR-002 [ACCESSIBILITY]: A statisztikai kártyák szövegei megfelelnek a WCAG 2.1 AA kontrasztkövetelményeknek (legalább 4.5:1 arány a háttérhez képest).
- NFR-003 [SECURITY]: Nincs külső, nem auditált CSS/JS könyvtár betöltése harmadik féltől származó CDN-ről.

## 7. UI-szerződés

- UI-001: `header-nav`, Header panel; állapotok: `sticky`, `glassmorphism`, `shadow-xl`.
- UI-002: `topic-sidebar`, Nav pill-tab konténer; állapotok: `overflow-x-auto`, `active-gradient`.
- UI-003: `detail-panel`, Detail kártyakonténer; állapotok: `idle`, `overview-grid`, `inspector-card`.
- UI-004: `map-canvas-frame`, 3D konténer; állapotok: `rounded-3xl`, `border-white/10`.
- UI-005: `stat-card-steuer`, Metric card; mutatja a százalékos értéket és forrást.
- UI-006: `stat-card-solar`, Metric card; mutatja a kWh/m² értéket és besorolást.
- UI-007: `ai-summary-card`, Executive Card; mutatja a generatív elemzést.

## 8. GUI-folyamat

1. A felhasználó betölti a főoldalt.
2. Megjelenik a teljes képernyős 3D Svájc térkép a lebegő fejléccel és a témaválasztó sávval.
3. Keresés után az áttekintő panelen kirajzolódik a 4 svájci statisztikai kártya és az AI összefoglaló.
4. A felhasználó a témasávban egy másik fülre (pl. "Planung") kattintva sima színátmenettel váltja a nézetet.
5. Egy építkezésre kattintva a mély-dosszié kártya tárja fel a kivitelezőt, építészt és a kockázati jelvényt.

## 9. Állapotmodell

Állapotok:
- IDLE: Alapértelmezett országos Svájc-nézet üveg HUD-dal.
- LOADED: Település betöltve, 4 stat-kártya aktív.
- INSPECTING: Egyedi építési projekt vagy mutató kijelölve a részletezőben.

Átmenetek:
- IDLE + search_success -> LOADED
- LOADED + select_item -> INSPECTING
- INSPECTING + clear_selection -> LOADED

## 10. Acceptance scenario-k

### AC-001: Lebegő HUD és 3D Térkép Megjelenés
Given a felhasználó megnyitja a főoldalt  
When a felület betöltődik  
Then a fejléc és a témasáv lebegő üveghatású (glassmorphism) stílusban jelenik meg  
And a 3D térkép kitölti a kerekített keretet

### AC-002: 4 Svájci Főmutató Kártya
Given érvényes település (pl. 8004 Zürich) ki van választva  
When az Overview fül aktív  
Then 4 különálló kártyán jelenik meg a Steuerfuss (%), Lärm (dB), ÖV (Klasse) és Sonnendach (kWh/m²)  
And megjelenik a kiemelt AI Executive Summary blokk

### AC-003: Pill-tab Témanavigáció
Given a főoldal nyitva van  
When a felhasználó a "Planung" fülre kattint  
Then a fül kék színátmenetes háttérre és fehér szövegre vált  
And a térkép és a lista azonnal a tervezési adatokra frissül

### AC-004: Baugesuch Deep Inspector Részletezés
Given a tervezési lista látható  
When a felhasználó rákattint egy építési projektre  
Then a részletező kártyán megjelenik az építtető, építész, övezet és a fellebbezési kockázati jelvény

### AC-005: 3D Tavak Csillogó Anyaga
Given a 3D térkép megjelenik  
When a felhasználó megvizsgálja a svájci tavakat (pl. Zürichsee, Lac Léman)  
Then a tavak áttetsző vízkék cián színnel és fényvisszaverődéssel jelennek meg

### AC-006: Mobilos Reszponzivitás és Görgetés
Given a felhasználó mobil képernyőn nyitja meg az oldalt  
When a témasávot ujjal jobbra-balra húzza  
Then a menüpontok simán, törésmentesen görgethetők anélkül, hogy a layout szétesne

## 11. API-szerződés

- Nem igényel új háttér-végpontot; a meglévő `/api/v1/place/{postcode}`, `/api/v1/politics`, `/api/v1/planning/baugesuche` és `/api/v1/ai/summary` válaszait rendereli modern statisztikai kártyákon.

## 12. Tesztleképezés

- REQ-001 -> AC-001 -> Playwright E2E teszt
- REQ-002 -> AC-002 -> Component és E2E teszt
- REQ-003 -> AC-002 -> Component teszt
- REQ-004 -> AC-003 -> Playwright E2E teszt
- REQ-005 -> AC-001 -> Visual regression teszt
- REQ-006 -> AC-003 -> Accessibility teszt
- REQ-007 -> AC-006 -> Performance és Mobile E2E teszt

## 13. Kockázatok és emberi döntések

- HR-001: A sötét üvegkontraszt és a betűméretek tipográfiai harmóniájának ellenőrzése.

## 14. Nyitott kérdések és Definition of Done

- Nincs implementációt blokkoló nyitott kérdés.
- DoD: Frontend TypeScript fordítás tiszta (0 error), Playwright és Pytest tesztek zöldek, a specifikációs validátor 100%-os lefedettséget igazol.
