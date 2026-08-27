# ADR-016: Építési Projektek Részletező & Kockázatelemző Panel (Baugesuch Deep Inspector)

- **Dátum:** 2026-08-27
- **Státusz:** accepted
- **Szerző:** System Architect & QA Lead (research: `docs/research/2026-08-27-baugesuch-deep-inspector.md`)
- **Kanban:** #swiss-p-map-016

## Kontextus
Jelenleg a kiválasztott építési projektekről csak az alap cím és dátum látható. Egy professzionális ingatlan- és térinformatikai platformon az építtető, a tervező építész, a parcellaszám, a zóna és a jogi fellebbezési határidő kockázata kulcsfontosságú.

## Döntés
1. **Részletes Domain Modell:** Bővítjük a `Baugesuch` modellt a következő opcionális mezőkkel:
   - `contractor`: Építtető cég vagy magánszemély
   - `architect`: Felelős építész iroda
   - `parcel_number`: Kataszteri azonosító / Assekuranznummer
   - `zone_type`: Építési zóna (pl. W3, K, GI)
   - `days_remaining`: Fennmaradó napok száma az Auflage határidőig
   - `risk_level`: Kockázati kategória (`low`, `medium`, `high`)
2. **Deep Inspector Kártya a Felületen:**
   - Amikor a felhasználó rákattint egy projektre a listában vagy a 3D térképen, a részletező panelen megjelenik a strukturált kártya.
   - Tartalmazza a határidő-státuszt (zöld ha >10 nap, sárga ha 5-10 nap, vörös ha <5 nap).
   - Közvetlen forráslink az `amtsblattportal.ch` hivatalos hirdetményéhez.

## Elvetve
| Opció | Miért nem |
|---|---|
| Külön felugró böngésző ablak (popup) | Blokkolhatja a böngésző és rontja a mobil használhatóságot |
| Csak nyers szöveges leírás | Nem engedi a strukturált keresést és a szűrést |

## Következmény
- Az építési projektek mély, szakmai szinten böngészhetők.
- A lakók és befektetők másodpercek alatt azonosíthatják a releváns fellebbezési határidőket.

## Kapcsolódó
- Research: `docs/research/2026-08-27-baugesuch-deep-inspector.md`
- Kód: `src/models/planning.py`, `src/services/ogd_service.py`, `frontend/src/app/[locale]/page.tsx`
- Következő ADR: ADR-017 (Interaktív Történeti Szavazási Idővonal)
