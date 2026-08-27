# Research — Többkantonos Építési Engedély Federáció (Bern, Basel, Genf)

- **Dátum:** 2026-08-27
- **Szerző:** architect & QA lead
- **Státusz:** draft → ADR-014 alapja
- **Kapcsolódik:** `src/services/planning_service.py`, `src/db/planning_repo.py`, `ADR-002`, `ADR-009`, `ADR-011`
- **Kérdés:** Hogyan bővíthető a Planning-pillér (építési engedélyek / Baugesuche) Zürichről országos szintre (Bern `3011`, Basel `4001`, Genf `1201`)?

---

## 1. Források kantononként

| Kanton | Hivatalos Közlöny / Portál | Formátum | Elérhetőség |
|---|---|---|---|
| **ZH (Zürich)** | Amtsblattportal + OGD 2982 | XML + CSV (22k) | Teljesen nyílt |
| **BE (Bern)** | Amtsanzeiger Bern / eBau BE | OGD / Amtsblattportal XML | Nyílt szövetségi kapu |
| **BS (Basel-Stadt)** | Kantonsblatt Basel-Stadt | Amtsblattportal XML | Nyílt szövetségi kapu |
| **GE (Genève)** | FAO (Feuille d'avis officielle) | Amtsblattportal XML | Nyílt szövetségi kapu |

Mindegyik kanton hivatalos közleményei (sub-rubric `BA` - Baugesuche) elérhetők a szövetségi `amtsblattportal.ch/api/v1/publications` végponton keresztül.

---

## 2. Megoldási Architektúra

1. **Kantonális Seed & Gyorstár:** A demo és induló állapot tartalmazza Bern (`3011`), Basel (`4001`) és Genf (`1201`) aktív minta-projektjeit valós koordinátákkal.
2. **Kantonális szűrő a PlanningService-ben:** A `planning_service.refresh(canton="BE")` és `canton="BS"` hívások a megfelelő kanton építési közleményeit kérik le.
3. **Frontend Integráció:** A Quick-Pick gombokra kattintva azonnal megjelennek a kantonhoz tartozó építési projektek mind a listában, mind a 3D térképen.
