# ADR-023: Watch-zone értesítési lánc és Einsprachefrist-menedzser

- **Státusz:** accepted (2026-09-24, implementálva: A `3edb777` + B `3370820`)
- **Dátum:** 2026-09-23
- **Kontextus:** research `docs/research/2026-09-23-proactive-civic-features.md`
- **Kapcsolódó:** ADR-002 (ingest), ADR-013 (3D pin), ADR-021 (radius watcher), SPEC-059/060

## Döntés

A meglévő ingest + watch-zone + push/newsletter elemeket **egy értesítési láncba**
kötjük, és mellé bevezetjük az **Einsprachefrist-menedzsert** (20 napos fellebbezési
határidő számonkérése). Nem vezetünk be új adatforrást — a meglévő Amtsblatt-adatra és
térbeli szűrőre építünk.

## Architektúra

1. **Matcher** (`WatchMatcher`): adott körzet-középpont + sugár → az ingest során
   tárolt Baugesuch-ok közül kiszűri az újakat. Determinisztikus, távolság-alapú.
2. **Esemény** (`WatchEvent`): `zone_id` + `baugesuch_id` + `distance_m` + `kind`
   (`new_permit`, `deadline_soon`). Minden esemény hordoz `source`/`fetched_at`/`trust_state`-et.
3. **Kézbesítés**: push előfizetés vagy e-mail (double opt-in) — mindkettő opcionális,
   a felhasználó választ. **Deduplikáció** `(zone_id, baugesuch_id, kind)` kulcsra.
4. **Einsprachefrist**: a `publication_date` + 20 nap → `deadline`, `days_left`,
   állapot (`open`, `due_soon ≤3 nap`, `expired`). Emlékeztető esemény a határidő előtt.

## Követelmények

- REQ-A1: értesítés csak a felhasználó által megadott zónára és consent mellett.
- REQ-A2: ugyanarra az eseményre ne menjen ki kétszer (dedup kulcs perzisztens).
- REQ-A3: minden esemény forrásolt (`source`, `fetched_at`, `trust_state`).
- REQ-B1: a fellebbezési határidő a publikáció dátumából számol, dokumentált szabállyal.
- REQ-B2: lejárt határidő nem jelenhet meg nyitottként; `due_soon` küszöb 3 nap.
- REQ-B3: a határidő-tájékoztatás nem jogi tanácsadás — disclaimer kötelező.

## Elvetett alternatívák

- **Új adatforrás (pl. fizetős API)**: nem szükséges, a meglévő ingest lefedi a célt;
  a szűk keresztmetszet a feldolgozás és kézbesítés, nem az adat.
- **Csak push, e-mail nélkül**: a VAPID-kulcs hiányában a push élesben nem működne,
  ezért a csatorna absztrakt (push | email), hogy a consent-lánc ma is használható legyen.
- **Esemény-alapú message broker**: aránytalan egy SQLite-alapú, egyszerű deploy-hoz.

## Hatás

- Új végpontok: `POST /api/v1/watch/zones`, `GET /api/v1/watch/events`,
  `GET /api/v1/watch/deadlines`, `POST /api/v1/watch/run`.
- FE: watch-zone kártya a hub-ban (események + határidő-visszaszámláló).
- Nem törő: a meglévő `/planning/radius` és push végpontok változatlanul maradnak.

## Kockázatok

- Push éles kézbesítés VAPID-kulcsot igényel → a csatorna addig `queued` állapotot ad,
  hamis "elküldve" visszajelzés nélkül (REQ-A3 szellemében).
- Kantononként eltérő fellebbezési szabály → a 20 nap ZH-alapú default, dokumentálva,
  későbbi bővítés kanton-táblával.
