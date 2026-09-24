# Proaktív civic funkciók — versenytárs-rés és következő feature-hullám

Dátum: 2026-09-23 · Módszer: Hermes natív VOC miner (6-létra) + competitor scout + saját kód-audit
Státusz: research kész → ADR-023 (proposed)

## 1. Kérdés

Mely funkciók adják a legtöbb értéket a következő hullámban, ha a cél a svájci lakosok
mindennapi döntéstámogatása (költözés, építkezés, helyi ügyek)?

## 2. Versenytárs-térkép (mért hatókör)

| Szereplő | Mit ad | Hol ér véget |
|---|---|---|
| swisstaxmap.ch | kanton-adó kalkulátor + térkép (4-5 nyelv) | csak adó, nincs hely/építés/életvitel |
| moneyland.ch | adó-rangsor, összehasonlítás | statikus cikk + kalkulátor, nincs hely-kontextus |
| comparis.ch | adó-összehasonlítás, ingatlan | nem önkormányzati ügyintézés, nem építés |
| houzy.ch — Baugesuche Pro | **proaktív értesítés** új építési kérelmekre ("Wissen, was gebaut wird. Bevor andere es wissen") | fizetős, csak Baugesuch, nincs többi életviteli réteg |
| geoda.ch | ingatlan-árbecslés címre | csak ár, nincs közösségi/civic réteg |
| amtsblatt-mcp / swisstopo-mcp | MCP-szerverek fejlesztőknek | nem végfelhasználói felület |

**Rés:** egyetlen szereplő sem fedi le együtt az **adó × építés × életvitel × proaktív
értesítés** négyest. A Swiss P Map 51 endpointja ma már ezt a négyest szolgálja ki
adatban — a hiányzó láncszem a **proaktív értesítés** és a **határidő-menedzsment**.

## 3. Belső kód-audit: mi van meg, mi lóg

| Réteg | Állapot | Bizonyíték |
|---|---|---|
| Baugesuch ingest (Amtsblatt XML) | ✅ élő | `POST /api/v1/connectors/amtsblatt/ingest`, `news/local` valós találat 8004-re |
| Watch-zone (térbeli szűrő) | ✅ él | `GET /api/v1/planning/radius`, `bbox`; FE `WatchZone.tsx` 300/500/1000/2000 m |
| Web Push előfizetés | ⚠️ **sziget** | `WebPushService.subscribe/alert` in-memory, nincs watch-zone kötés |
| Newsletter double opt-in | ⚠️ **sziget** | `NewsletterService` kész, nincs esemény-kiváltó |
| Einsprache (fellebbezés) | ⚠️ **részleges** | `objection_workspace_service` sablon van, **határidő-számítás nincs** |
| Provenance / trust | ✅ él | `SourceTrustBadge`, `/system/sources-provenance` |

**Következtetés:** nem új adatforrás kell, hanem a meglévő elemek **összekötése** —
értesítési lánc az ingest és a watch-zone között, plusz a 20 napos Einsprachefrist
számonkérése, ami a legfájdalmasabb svájci eljárási pont.

## 4. Fájdalompontok (verbatim irányok a forrásokból)

- houzy Baugesuche Pro pozicionálása: *"Wissen, was gebaut wird. Bevor andere es wissen."*
  → a felhasználói érték nem az adat, hanem az **időbeli előny**.
- SRF: *"Einsprachen – die fünfte Landessprache der Schweiz?"* → a fellebbezés
  mindennapi, tömeges jelenség; a **határidő** elmulasztása visszafordíthatatlan.
- geoda: az ár önmagában kevés — *"users care about the likely total price of a similar
  home, not just the unit price"* → kontextus + becslés együtt kell.
- moneyland: Zug 70 000 CHF jövedelemre <3000 CHF adó vs. Neuchâtel >11 000 CHF
  → az önkormányzati különbség **drámai**, ezért a hely-szintű összehasonlítás értékes.

## 5. Feature-jelöltek (érték × költség × kockázat × karbantarthatóság, 1-5)

| # | Feature | Érték | Költség | Kockázat | Karbant. | Össz |
|---|---|---|---|---|---|---|
| A | **Watch-zone → értesítési lánc** (ingest → matcher → push/e-mail, dedup) | 5 | 3 | 2 | 4 | **17** |
| B | **Einsprachefrist-menedzser** (20 napos számláló + emlékeztető + sablon) | 5 | 2 | 2 | 5 | **16** |
| C | **ÖREB zóna élő lekérdezés** (geodienste.ch OGC API → mi építhető a címre) | 4 | 3 | 3 | 3 | 13 |
| D | **Körzet-változás feed** ("mi változott a körzetemben") | 3 | 3 | 2 | 4 | 12 |

Sorrend: **A → B → C → D.** Az A ad retenciót (visszatérő használat), a B ad
megelőzhető kárt (jogvesztés), a C ad adatmélységet, a D ad hosszú távú kötődést.

## 6. Ajánlás

Az **A + B** páros együtt szállítandó: az A megtalálja az eseményt, a B megmondja,
mit kell vele tenni és meddig. Ez a houzy-propozíciónál szélesebb (nem csak építés),
és a jogi határidő miatt erősebb értékajánlat, mint a puszta értesítés.

Részletek: `docs/decisions/ADR-023-watch-zone-alert-pipeline.md`.

## 7. Korlátok / nyitott kérdések

- Valós push-kézbesítés VAPID-kulcsot igényel (env), éles csatorna még nincs bekötve.
- Az e-mail csatorna SMTP-t igényel (env), a double opt-in lánc kész.
- Az ÖREB lekérdezés kantononként eltérő végpontot használhat — pilot ZH-val indul.
