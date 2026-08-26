# ADR-001: Technológiai Stack és Rendszerarchitektúra Kiválasztása

- **Dátum:** 2026-08-26
- **Státusz:** accepted
- **Szerző:** analyst (research: `docs/research/2026-08-26-kickoff.md`, competitor: `docs/competitor/2026-W35-scan.md`)
- **Kanban:** #swiss-p-map-001

## Kontextus
A **Swiss P Map** pozicionálása: **„A svájci környék egyetlen térképén”** — a három pillér (**Politics × Place × Planning**) egyedülálló keresztmetszete.
A W35-ös versenytárselemzés feltárta, hogy a *Planning* önálló riasztási piacát (Baugesuch-alert) a Houzy Pro (B2C) és a smartconext (B2B) már lefedi, ráadásul a zürichi építési kérelmek csak a 20 napos *Auflage*-ablakban nyilvánosak (áramló adat).
Ezért a rendszer nem izolált értesítő alkalmazásként indul, hanem a **Politics + Place** stabil, versenytárs-mentes OGD alapjaira épülő térképes platformként, amely a 2. fázisban integrálja az áramló Planning adatokat.

## Döntés
Az **Opció A: Modern Web App (Next.js + MapLibre GL JS + Python ETL Backend)** architektúrát választjuk az alábbi prioritásokkal:

1. **MVP Fázis 1 (Politics + Place):**
   - **Frontend & Térkép:** Next.js (TypeScript / Tailwind CSS) + **MapLibre GL JS** hardveresen gyorsított WebGL vektoros kliens, hivatalos Swisstopo vektoros stílusokkal (`vectortiles.geo.admin.ch`).
   - **Politics:** Városi és kantonális képviselők (*PARIS-API*, *Kantonsrat OGD*), benyújtott indítványaik (*Vorstösse*), lobbi- és érdekeltségi kapcsolataik (*Lobbywatch*).
   - **Place:** Községi adókulcsok (*Steuerfuss*), zajterhelés (*sonBASE*), közösségi közlekedési minőség (*ÖV-Güteklassen*), épületregiszter (*GWR*).
   - **AI Réteg:** Claude / Gemini LLM Gateway a képviselői indítványok és helyi ügyek egyszerű nyelvi összefoglalására (DE, FR, IT, EN).
2. **Fázis 2 (Planning):**
   - Áramló 20 napos építési kérelem feed (*Amtsblattportal API*, *eAuflageZH*) és zónabesorolás (*ÖREB M2M Webservice*).
3. **Backend & Adattár:**
   - Python 3.11+ (FastAPI, Shapely, PyProj a svájci LV95/EPSG:2056 $\leftrightarrow$ WGS84 koordinátaváltáshoz).
   - PostgreSQL + PostGIS (térbeli indexelés és sugaras körzetlekérdezések: `ST_DWithin`).

## Elvetve
| Opció | Miért nem |
|---|---|
| **Izolált Baugesuch Alert App** | A Houzy és smartconext mellett kudarcra ítélt; a valódi versenyelőny a három pillér térképes fúziója. |
| **Mobil Natív App (Flutter / React Native)** | Magasabb kezdeti fejlesztési költség, zárt app store jóváhagyások, nehézkes megoszthatóság. |
| **Mapbox GL JS (Kereskedelmi)** | Költséges licencdíj; a MapLibre 100% nyílt forráskódú és natívan kezeli a Swisstopo stílusokat. |

## Következmény
- **Scaffold feladatok:**
  - `src/` modularizált mappa-struktúra (Python ETL/API + frontend térképes kliens).
  - `tests/` tesztkörnyezet kiépítése (unit tesztek a koordináta-konverzióra és OGD kliensekre, E2E keret).
  - CI workflow (`.github/workflows/ci.yml`) automatikus teszteléssel és típusellenőrzéssel.
- **Fejlesztési szabályok:** Max 3 fájl / lépés szabály, RED $\rightarrow$ GREEN tesztvezérelt implementáció.

## Kapcsolódó
- Research: `docs/research/2026-08-26-kickoff.md`
- Competitor: `docs/competitor/2026-W35-scan.md`
- Következő ADR: `docs/decisions/ADR-002-data-ingestion-pipeline.md`
