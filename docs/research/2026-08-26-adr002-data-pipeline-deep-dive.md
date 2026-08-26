# ADR-002 Deep Dive — Adat-pipeline: stub → valós OGD (Hermes natív miner + resilient)

> **Dátum:** 2026-08-26 | **Státusz:** draft (evaluatorral rangsorolva, ADR-002-be emelhető)
> **Ledger:** `/tmp/ledger-deep-2026-08-26.json` | **Minerek:** Hermes natív (web_search + jina), Gemini `no data — quota` (nem blokkol)
> **Kapcsolódik:** `ADR-001`, `docs/research/2026-08-26-kickoff.md`, `docs/competitor/2026-W35-scan.md`, `src/services/*.py` stubok

## 1) Hermes natív VOC bányászat — eredmény (resilient: Gemini kvóta, web_extract gateway hiba → jina fallback)

| # | Forrás | Verbatim (szó szerint vagy search snippet — forrás-hű) | Kontextus | Dátum | URL | Érzelem | Téma |
|---|---|---|---|---|---|---|---|
| 1 | Houzy.ch | „Baugesuche Pro – Alle aktuellen Baugesuche in Ihrer Umgebung auf einen Blick” | Landing headline, B2C alert positioning | 2026-08-26 scrape | https://www.houzy.ch/funktionen/baugesuche [1] | neutral | desired_outcome |
| 2 | smartconext | „In der Schweiz werden jährlich gut 70'000 Baugesuche eingereicht. Der smartconext PORTFOLIO ALERT filtert aus Millionen von Daten exakt die Projekte, die für Ihr Immobilienportfolio relevant sind.” | B2B portfolio alert pitch | 2026-08-26 scrape | https://www.smartconext-bau.ch/de/loesungen/portfolio-alert/ [2] | neutral | JTBD |
| 3 | Lobbywatch | „Die umfangreichste Lobby-Datenbank der Schweiz — Eine Recherche-Ressource zu politischen Netzwerken” | Lobby DB mint kutatási eszköz | 2026-08-26 scrape | https://lobbywatch.ch/lobbydatenbank/ [3] | neutral | alternative |
| 4 | OpenParlData | „We currently publish our data under the Creative Commons Licence CC BY 4.0. Please attribute as: Source: OpenParlData.ch” | PARIS harmonizált parlamenti adatok licenc | 2026-08-26 scrape | https://api.openparldata.ch/documentation [4] | positive | alternative |
| 5 | BAFU/sonBASE | GIS-Lärmdatenbank sonBASE (tájékoztató oldal, zaj-adatbázis) | Zajterhelés OGD forrás | 2026-08-26 search hit | https://www.bafu.admin.ch/de/sonbase [5] | neutral | JTBD |
| 6 | opendata.swiss ÖV | „Public transport quality categories (ARE)” — ÖV-Güteklassen dataset | Tömegközlekedési minőség OGD | 2026-08-26 search hit | https://opendata.swiss/en/dataset/ov-guteklassen-are1 [6] | neutral | JTBD |
| 7 | Trustpilot Houzy | „Houzy AG is rated Great with 3.9 / 5 on Trustpilot” | Houzy elégedettség jel (nem 1-3★ panasz, hanem átlag) | 2026-08-26 scrape | https://www.trustpilot.com/review/houzy.ch | neutral | praise |
| 8 | Reddit r/Switzerland | „Airconditioners (splits) banned for home use in lot of swiss ...” (Baugesuch-kapcsolt szabályozási pain) | Baugesuch-szabályozás körüli frusztráció | 2024-08 search hit | https://www.reddit.com/r/Switzerland/comments/1en5d9x/airconditioners_splits_banned_for_home_use_in_lot_of_swiss/ | frustrated | pain |
| 9 | Reddit r/askswitzerland | „Where to live when working in Zug with a ~CHF 2.5k housing budget?” | Lakáskeresés Zürich-környéki pain (ár + lokáció) | 2026 search hit | https://www.reddit.com/r/askswitzerland/comments/1mx0e22/where_to_live_when_working_in_zug_with_a_chf_2_5k_housing_budget/ | frustrated | pain |
| 10 | Comparis Steuervergleich | „Steuern vergleichen und sparen” — Steuerfuss összehasonlító | Adókulcs-összehasonlítás mint user JTBD | 2026-08-26 search hit | https://www.comparis.ch/steuern/steuervergleich/default | neutral | JTBD |
| 11 | Gemini Reddit+HN | `no data — gemini quota exhausted` (3 retry, 0s reset ígéret nem jött) — nem blokkol, Hermes adatból dolgozunk | — | 2026-08-26 | — | — | — |
| 12 | Gemini PH+Reviews | `no data — gemini quota exhausted` — resilient fallback Hermes-hez | — | 2026-08-26 | — | — | — |
| 13 | web_extract (nous gateway) | `not entitled or unreachable` — jina fallback sikerült helyette | — | 2026-08-26 | — | — | — |

**Top 3 pattern (freq×intensity):**
- **Baugesuch-alert létező piac** — 70k/év, Houzy B2C + smartconext B2B már fedi listaként, nem térképként.
- **Adó+lakhatás JTBD erős** — Steuerfuss-összehasonlítás + 2.5k CHF budget pain külön forrásokban.
- **Politika-háló átláthatóság** — Lobbywatch „umfangreichste” pozicionálása jelzi az igényt, PARIS CC-BY 4.0 legálisan használható.

**Resilience jegyzet:** Gemini 2× párhuzamos kvóta-fal, web_extract gateway hiba — mindkettő `no data` és jina fallbackel pótolva, a kiértékelés nem blokkolt.

## 2) Kiértékelő — deduplikálás + klaszter + ötlet-jelöltek

Klaszterek (pain/JTBD/feature-gap):

| Klaszter | Források | freq×intensity | Gap (van-e konkurens?) |
|---|---|---|---|
| Baugesuch alert (Planning) | Houzy + smartconext + Reddit szabályozás | 4 | kicsi gap — lista/alert van, térkép-first nincs |
| Steuerfuss + lakhatás (Place) | Comparis + Reddit budget + Steuerfuss OGD | 3 | közepes gap — összehasonlító van, de nem térképen + politikával együtt |
| Zaj + ÖV minőség (Place) | sonBASE + ÖV-Güteklassen + Reddit zaj-panasz (közvetett) | 2 | nagy gap — senki nem mutatja térképen együtt |
| Politika-háló (Politics) | Lobbywatch + PARIS API | 2 | nagy gap — Lobbywatch táblázat, de nincs térkép + AI összefoglaló |

## 3) Ötlet-jelöltek → pontozás (1-5 rubrika, súlyozott prioritás)

Súly: Kereslet 30% + Gap 25% + Hatás 20% + Megvalósíthatóság 15% + Bevétel 10%

| Rank | Ötlet | Kereslet | Gap | Hatás | Megvalósíthatóság | Bevétel | Prioritás | Top bizonyíték | Következő lépés |
|---|---|---|---|---|---|---|---|---|---|
| 1 | **Place-first térkép: Steuerfuss + sonBASE + ÖV egy kattintásra** | 4 | 5 | 4 | 4 (stabil OGD, statikus) | 3 | **4.15** | [5][6] + Comparis JTBD + Reddit budget pain | Research mélyítés: sonBASE licenc + ÖV CSV schema → ADR-002 → kártya: `place_service` OGD kliensek |
| 2 | **Politics-háló térképen + AI 5 nyelven** (képviselő + Lobbywatch + Vorstösse összefoglaló) | 3 | 5 | 5 | 3 (PARIS CC-BY OK, Lobbywatch scrape engedély kérdés) | 3 | **3.95** | [3][4] | Research: PARIS API próbahívás + Lobbywatch ToS → ADR-002 → kártya: `politics_service` valós kliens |
| 3 | **Baugesuch térkép-first (nem alert)** — parcella-szint böngészés, 20 napos feeddel | 4 | 3 | 4 | 2 (áramló adat, csak 20 nap Auflage ablak, nem archív) | 4 (alert piac fizet) | **3.40** | [1][2] 70k/év | Halasztva Fázis 2-re (ADR-001 szerint) — Research: Amtsblattportal API próba |
| 4 | **Lakhatás-budget kalkulátor** (Steuerfuss + bérleti díj becslés + ÖV) | 4 | 3 | 3 | 3 | 2 | 3.20 | Reddit 2.5k CHF + Comparis | Backlog — Place után |
| 5 | **Trustpilot/review aggregátor** (Houzy 3.9/5 kontextus) | 2 | 4 | 2 | 4 | 1 | 2.60 | Houzy 3.9/5 | Nem prioritás — nincs JTBD |

## 4) Top 5 részletezés (grooming-ready)

### #1 Place-first térkép (Steuerfuss + sonBASE + ÖV)
- **Pitch:** Zürich-környéki lakáskereső egy térképen látja: mennyi adó, mennyire zajos, milyen az ÖV — amit ma 3 helyen kell összevadászni.
- **Bizonyíték:** „70'000 Baugesuche” kontextus mutatja az adat-éhséget [2]; Steuerfuss-összehasonlítás JTBD (Comparis); Reddit 2.5k budget pain.
- **Kockázat:** sonBASE licenc + frissítési gyakoriság tisztázandó; ÖV CSV schema változhat.
- **Következő:** `docs/research/2026-08-26-place-ogd-deep-dive.md` (sonBASE + ÖV schema próba) → `ADR-002` Place rész → kártya: `feat: Place OGD kliensek (Steuerfuss/zaj/ÖV) — ZH pilot`

### #2 Politics-háló térképen + AI
- **Pitch:** Választókerületi képviselő + lobbikapcsolat + indítvány AI-összefoglalója egy kattintásra, térképen — senki nem adja így.
- **Bizonyíték:** Lobbywatch „umfangreichste Lobby-Datenbank” [3]; PARIS CC-BY 4.0 legális [4].
- **Kockázat:** Lobbywatch scrape vs. API — ToS ellenőrzés kell; Vorstösse többnyelvűség.
- **Következő:** `docs/research/2026-08-26-paris-lobbywatch-probe.md` → `ADR-002` Politics rész → kártya: `feat: Politics OGD kliens (PARIS + Lobbywatch)`

### #3 Baugesuch térkép-first (Fázis 2)
- Halasztva — lásd ADR-001. Kockázat: 20 napos Auflage ablak, nem archív → feed-architektúra kell, nem CRUD.

## 5) Javasolt ADR-002 váz (stub → valós sorrend)

1. **Elsőnek: Place OGD** (Steuerfuss, sonBASE, ÖV) — stabil, statikus, nagy gap, azonnali user value.
2. **Másodiknak: Politics OGD** (PARIS + Lobbywatch) — CC-BY tiszta, de scrape-jogi + AI réteg miatt második.
3. **Harmadiknak: Planning áramló** (Amtsblattportal 20 nap) — Fázis 2, külön feed-architektúra.
4. Minden lépés: élő API próbahívás → schema rögzítés → `src/services/*` csere stub→valós → E2E.

## Sources

[1] https://www.houzy.ch/funktionen/baugesuche
[2] https://www.smartconext-bau.ch/de/loesungen/portfolio-alert
[3] https://lobbywatch.ch/lobbydatenbank
[4] https://api.openparldata.ch/documentation
[5] https://www.bafu.admin.ch/bafu/de/home/themen/laerm/fachinformationen/laermbelastung/laerm-datenbank-sonbase.html
[6] https://opendata.swiss/en/dataset/ov-guteklassen-are1
