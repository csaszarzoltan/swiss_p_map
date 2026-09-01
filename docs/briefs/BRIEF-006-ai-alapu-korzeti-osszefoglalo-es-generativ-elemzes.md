# BRIEF-006: AI-Alapú Körzeti Összefoglaló és Generatív Elemzés

**Státusz:** READY_FOR_SPEC  
**Kapcsolódó feature:** FEAT-006 (ADR-006)  
**Forrás:** az AI summary gateway szolgáltatás, a Pydantic adatmodellek és a 4 nyelven generált narratív összefoglalók alapján

## Probléma

A felhasználók számára a száraz számadatok (dB értékek, adókulcs százalékok, engedélyek száma) önmagukban nehezen értelmezhetők. Szükség van egy érthető, emberi nyelven megfogalmazott intelligens vezetői összefoglalóra ("Executive Summary"), amely kontextusba helyezi a körzet adatait.

## Célcsoport és kontextus

Családok, ingatlanvásárlók és döntéshozók, akik gyorsan meg akarják érteni egy település vagy kerület összképét (életminőség, költségek, fejlesztési aktivitás).

## Kívánt eredmény

Egy gombnyomásra elérhető, AI-alapú szöveges értékelés a kiválasztott nyelven (DE, EN, FR, IT), amely összefüggéseiben magyarázza el a Steuerfusst, a zajszintet, a közlekedést és a folyamatban lévő építkezéseket.

## Jelenlegi / Tervezett funkciókat lefedő felhasználói történetek

- **US-006-01:** Felhasználóként szeretnék az áttekintő panelen egy 3-4 mondatos AI összefoglalót kapni a keresett körzetről.
- **US-006-02:** Nyelvváltáskor szeretném, hogy az AI összefoglaló automatikusan az aktív nyelven jelenjen meg.
- **US-006-03:** Rendszerként szeretném, hogy ha a külső LLM gateway nem elérhető, egy determinisztikus sablon-alapú összefoglaló azonnal helyettesítse.

- **US-006-04:** Felhasználóként szeretném egyértelműen látni, ha az összefoglaló sablonból és nem élő LLM-válaszból származik, hogy ne tévesszem össze a két forrást.

## Scope

- `POST /api/v1/ai/summary` végpont (`locale`, `postcode`, `place`, `politics`, `baugesuche` paraméterekkel).
- `AiSummaryService` aszinkron HTTP klienssel és hibatűrő fallback logikával.
- Frontend AI badge és intelligens szövegmegjelenítő.

## Non-scope

- Felhasználó által tetszőlegesen beírt promptok szabad csevegőablaka (a fókusz a strukturált összefoglaláson van).

## Érintett rendszerek

- `src/services/ai_summary_service.py`, `src/main.py`, `frontend/src/app/[locale]/page.tsx`

## Bizonytalanságok

- LLM válaszidők és token költségek optimalizálása (gyorstárazás és timeout kezelés).
