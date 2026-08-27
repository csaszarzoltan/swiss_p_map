# ADR-020: Kockázatjelzés + „Miért" Indoklás (Risk Badge)

- **Dátum:** 2026-08-28
- **Státusz:** accepted (jövő heti backlog #2)
- **Szerző:** researcher (research: `docs/research/2026-08-28-usability-deep-dive.md` Rank #2)
- **Kanban:** #swiss-p-map-020 — P0 | Epic: Planning UX

## Kontextus

A Planning pillér bejegyzései azonos listaelemként látszanak, súlyozás nélkül a user nem tudja melyik „veszélyes" a környékére [3][4]. A jogi Auflagé ablak 20 napja alatt a kockázat láthatóvá tétele a felhasználó számára a legmagasabb hatású üzenet. A BFS/ODA open-data rétegek (`opendata.swiss/de/dataset`) a forrás-hitelesítést mutatják [4].

## Döntés

1. **Backend:** `src/models/place.py` + `RiskScore` (low/medium/high) mező meglévő `risk_level`-re hivatkozva (place_service már `Kernzone → high` heurisztikával él — bővítés, nem új modell). `src/services/place_service.py` kiegészítés: indoklás-mondat (`risk_reason`) [3].
2. **Frontend:** `frontend/src/components/RiskBadge.tsx` (~80 sor) — színkód (zöld/amber/piros) + tooltip „Miért?" szöveg + ikon [2]; a `DetailPanel` használja majd, `messages/*.json` +4 kulcs.
3. **Adatkapu:** nincs új endpoint; a már élő `GET /api/v1/place/{postcode}?live` kibővítésével (backward-compatible) [3][4].

## Elvetve

| Opció | Miért nem |
|---|---|
| ML modell score (LLM) | Cooldown alatt `502 ai_unavailable` [ADR-006] — nem stabil |
| Külön risk endpoint | Felesleges round-trip; place response már hordozza |

## Következmény

- Kártya: `place_service.py` 400→bővítés + `RiskBadge.tsx`; max 400 sor/file.
- Validálás: `pytest -q` (risk_score sémateszt) + `npm run build` + E2E `risk badge visible` (us_020_risk).
- Biztonság: nincs auth, read-only, literálok nem interpolálódnak (XSS-safe).

## Kapcsolódó

- Research: `docs/research/2026-08-28-usability-deep-dive.md` (Rank #2)
- Kód: `src/services/place_service.py`, `frontend/src/components/RiskBadge.tsx`
- Következő ADR: ADR-021 (Radius watcher)
