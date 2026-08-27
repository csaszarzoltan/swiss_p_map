# ADR-022: Megosztható Mélylink + Nyelv-Perzisztencia (Deep-Link Share)

- **Dátum:** 2026-08-28
- **Státusz:** accepted (jövő heti backlog #4)
- **Szerző:** researcher (research: `docs/research/2026-08-28-usability-deep-dive.md` Rank #4)
- **Kanban:** #swiss-p-map-022 — P1 | Epic: Share & i18n

## Kontextus

Az i18n most `always` prefix-szel 3320 helyett 3410-en futhat locale-újraterítéssel, a `messages/*.json` mind a 4 nyelven zöld [4]. A share deep-link még nincs linkelve: a kiválasztott `plz + topic + selectedId` nem perzisztens URL-ben. A `opendata.swiss/de/dataset` minta megosztható dataset-linket mutat [4], az Amtsblattportálon a `build version: 1.18.14` alatt élő radius a perzisztencia jó párhuzama [5]. Houzy share-link igen [2], ezért a hiány feature-gap.

## Döntés

1. **State → URL:** `frontend/src/hooks/useShareableState.ts` / `frontend/src/app/[locale]/page.tsx` kiegészítés — `?plz=8004&topic=planung&selected=demo-8004-1&radius=500` a kiválasztás után `history.replaceState`-tel perzisztens, `Copy link` gombbal másolható [4][5].
2. **URL → State:** page mount-kor parse `searchParams` + `router.replace` (next-intl `useRouter`) — language-aware, locale perzisztencia jó [4].
3. **Komponens:** `ShareButton.tsx` (~60 sor) + `messages/*.json` +4 kulcs; max 60 sor, 0 backend.

## Elvetve

| Opció | Miért nem |
|---|---|
| LocalStorage only | Nem megosztható (személyes device), FO leak veszély [4] |
| Server-side set-cookie per topic | Felesleges round-trip; state a böngészőben tisztább |

## Következmény

- Kártya: `hooks/useShareableState.ts` + `ShareButton.tsx` + `page.tsx` hook-bekötés; max 3 file / lépés.
- Validálás: E2E `copy link -> new tab same state` (us_022_share) + `npm run build` + `mypy` nem változik.
- Biztonság: query literálok nem interpolálódnak (XSS-safe), `postcode` 4-jegy validálás [2].

## Kapcsolódó

- Research: `docs/research/2026-08-28-usability-deep-dive.md` (Rank #4)
- Kód: `frontend/src/hooks/useShareableState.ts`, `frontend/src/components/ShareButton.tsx`, `frontend/src/app/[locale]/page.tsx`
- Következő ADR: — (jövő hét lezárva)
