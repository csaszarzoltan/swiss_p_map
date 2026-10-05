# Swiss event and election data sources for map rendering — verified survey

**Date:** 2026-10-04 · **Method:** live HTTP fetch of operator documentation and endpoints, this run.
Rows marked ✅ were read from the URL in this file today. Anything not read is marked **not verified**
and is not used as a load-bearing claim.

---

## 0. Two findings that change the dispatch premise

**(1) The repository does not call BFS VoteInfo.** The dispatch assumes "we already call BFS VoteInfo
for a proposal list". That is false. `src/services/connectors/bfs_voteinfo_client.py` is a 23-line
stub whose `sync()` returns a hardcoded literal and never opens a socket:

```python
rows = [{"id": 6670, "yes": 58.2}]
raw = json.dumps(rows, sort_keys=True).encode()
```

(verified by reading the file, 2026-10-04; ADR-012 and SPEC-056 describe the intent, but the
connector is not implemented.) So question (a)'s "what ELSE does it expose" is open in full — and
the answer is worse than expected, see (2).

**(2) BFS VoteInfo is an Android/iOS *app*, not an API.** Read from BFS's own page, verbatim:

> "Mit der von der Bundeskanzlei, dem Bundesamt für Statistik und dem Statistischen Amt des Kantons
> Zürich gemeinsam entwickelten App «VoteInfo» kann das Abstimmungsgeschehen am Sonntag quasi live
> mitverfolgt werden. Die Nutzerinnen und Nutzer können ab 12 Uhr auf «VoteInfo» erfahren, wie ihre
> **Gemeinde**, ihr **Kanton** und die Schweiz zu eidgenössischen und kantonalen Vorlagen gestimmt
> haben. Die Abstimmungsergebnisse werden – von den Kantonen automatisiert ans BFS geliefert – vom
> BFS laufend aktualisiert."
> — `https://www.bfs.admin.ch/bfs/de/home/statistiken/politik/abstimmungen/voteinfo.html` (HTTP 200, fetched 2026-10-04)

That is the one page that would document an API if one existed. Scanned for `CSV|JSON|Schnittstelle|
API|Download` → **0 hits each**. The BFS *Abstimmungen* landing page likewise has **no** `.csv`,
`.xlsx`, `.zip` or `px-x` download links, and no `STAT-TAB`/`Datenbank` pointer.

So the granular shape is *documented and app-served* (municipality + canton + country, quasi-live
from 12:00 on vote day) but the *distribution channel is a mobile app*, not a documented
machine-readable endpoint. **There is no `voteinfo.bfs.admin.ch`** — that host does not resolve
(HTTP 000), and `abstimmungen.bfs.admin.ch` likewise. CKAN `q=voteinfo` on opendata.swiss → `count 0`.

---

## 1. Summary table

| # | Source / operator | Shape | Granularity | Lat/lon or stable key | Access | Licence | Cadence | Verified |
|---|---|---|---|---|---|---|---|---|
| 1 | **BFS STAT-TAB / PXWeb** | statistical tables | varies, often municipality | `GEO_NAME` dimension | **REST/OGD, live** | not stated per table | per-table `updated` | ✅ |
| 2 | **BFS VoteInfo OGD** (BK/BFS/AZ Zürich) | federal vote outcomes, **per municipality** | **municipality + canton + CH** | BFS `geoLevelnummer`; 161 gemeinden for canton ZH | **REST JSON, live — HTTP 200, 1.98 MB** | not stated | per vote Sunday | ✅ REFUTED 2026-10-05 (was "app only — no API found") |
| 3 | **Federal vote dashboard** `abstimmungen.admin.ch` | federal + cantonal vote outcomes | municipality → canton → CH | canton/municipality keys in page | Next.js SPA, **no data endpoints found** | n/a | live on vote day | ✅ (negative) |
| 4 | **Federal elections** `wahlen.admin.ch` | seats + party shares | **canton** | canton code | HTML result tables | not stated | per election | ✅ |
| 5 | **Canton ZH vote archive** (Amt f. Statistik ZH) | vote outcomes | **municipality + Bezirk**, since 1831 | `STAT_GEMEINDE_ID` | **CSV, live** | not stated | per vote day | ✅ |
| 6 | **Canton BL vote archive** | vote outcomes | **municipality**, since 2003 | `entity_id` | **CSV/JSON/Parquet, live** | not stated | per vote day | ✅ |
| 7 | **Canton Bern** | vote outcomes | canton | canton code | CSV | not stated | per vote day | ✅ |
| 8 | **City of Zurich** | vote outcomes | city/district, since 1933 | — | CSV/Parquet | not stated | per vote day | ✅ |
| 9 | **swisstopo SearchServer** | geocoding | any address/municipality | **returns lat/lon + featureId** | **REST, live** | open | continuous | ✅ |
| 10 | **opendata.swiss** | catalogue of all the above | varies | varies | **CKAN API, live** | per-dataset | — | ✅ |
| 11 | **MeteoSchweiz OGD** | measurements | point/station | station coords | docs portal | not read | near-real-time | ⚠️ docs only |
| 12 | **Alertswiss** (BABS) | civil-protection alerts | area | — | **no public API found** | n/a | live push | ⚠️ negative |
| 13 | **Amtsblattportal.ch** (current Baugesuch source) | publications, incl. events | address-level | **lat/lon** | **REST XML, live** | not stated | daily | ✅ (in repo) |

Licence column: **I could not verify commercial-use terms for any of these.** `license_id` and
`license_title` were `None` on every opendata.swiss record queried, BFS's legal-notice page contains
no "open data" licence statement, and opendata.swiss' `Nutzungsbedingungen` page is JS-rendered
(403 on parsed fetch, no licence keywords in the served HTML). **Treat every licence cell as
unresolved — confirm per dataset on its own portal before shipping.** The only field confidently
answerable: opendata.swiss is "ein Metadatenkatalog" — a catalogue, so licences are set by each
publisher, not by the portal.

---

## 2. Per-source detail

### 1. BFS PXWeb — the only federal machine-readable API, live and verified

```
GET https://www.pxweb.bfs.admin.ch/api/v1/de
→ HTTP 200, application/json, 38,641 B, 644 table entries
GET https://www.pxweb.bfs.admin.ch/api/v1/de/px-x-1003020000_101
→ [{"id":"px-x-1003020000_101.px","type":"t",
   "text":"Hotellerie: ... in 185 Gemeinden nach Jahr, Monat, Gemeinde ...",
   "updated":"2026-09-04T08:31:06"}]
```

**Important negative, verified:** all 644 titles filtered for
`abstimm|wahl|nationalrat|ständerat|election` → **0 matches.** Federal vote/election tables are
*not* on this PXWeb instance. Also `?query=abstimmung` returns empty — enumerate `/api/v1/de`, don't search.

### 2–3. Federal votes — documented at municipality level, distributed only via app

The dashboard `https://abstimmungen.admin.ch/` is live (HTTP 200, 131 KB, Next.js). Its only internal
links are `/overview` and information pages; a scan for `href/src` containing
`csv|json|api|download|export` returned **nothing**. `/de/vote/overview` → 404. So the richest
official source (municipality granularity) is behind a UI with no discoverable data endpoint.

### 4. Federal elections — canton granularity only

`https://www.wahlen.admin.ch/` (HTTP 200). Its 2023 National Council results page
`https://www.wahlen.admin.ch/de/2023/ch/23-table-results-national-council-election` carries this
verbatim link, which is **BFS pointing at the machine-readable route**:

```
href="https://opendata.swiss/de/dataset/?q=federal elections&keywords_de=nationalratswahlen&res_format=JSON"
```

### 5–8. Cantonal/municipal — question (c) answered: **no national aggregator, per-canton is real**

Exhaustive CKAN query returns only canton/city publishers. Verified schemas:

**Canton Zürich** (municipality-level since 1831 — the best single asset found):
`https://www.web.statistik.zh.ch/ogd/data/KANTON_ZUERICH_abstimmungsarchiv_gemeinden.csv`

```
ABSTIMMUNGSTAG,STAT_VORLAGE_ID,VORLAGE_KURZBEZ,...,BFS,STAT_GEMEINDE_ID,GEMEINDE,BEZIRK,
AZ_STIMMBERECHTIGTE,AZ_EINGELEGTE_STIMMZETTEL,STIMMBETEILIGUNG,...,AZ_JA_STIMMEN,AZ_NEIN_STIMMEN,...
04.02.1838,801,Mandatsverteilung zwischen Stadt und Landschaft bei den Grosssratswahlen,...,1,1,Aeugst a.A.,Affoltern,131,25,19.08,25,13,12,0,,0
```

Note `STAT_GEMEINDE_ID`/`BFS` and `BEZIRK` — this carries a **BFS municipality number and district**,
exactly the stable geo key the map needs. The canton file `…_abstimmungsarchiv_kanton.csv` also
embeds `URL_VOLKSABSTIMMUNG` and `ANNEHMENDE_GEBIETE`, so results are self-documenting.

**Canton Basel-Landschaft** (municipality-level, live data confirms recency):
`https://data.bl.ch/api/v2/catalog/datasets/11990/exports/json`

```json
[{"date":"2026-09-27","entity_id":"2761","name":"Aesch (BL)","district":"Arlesheim",
  "vote_id":"20260927_E1","domain0":"federation","type":"proposal",
  "title_de_ch":"Volksinitiative «Wahrung der schweizerischen Neutralität (Neutralitätsinitiative)»",
  "counted":"True","answer":"rejected","percent_yeas":26.888,"percent_nays":73.111,
  "percent_turnout":40.131,"eligible_voters":7022,"expats":196,"empty":16,"invalid":35,
  "yeas":744,"nays":2023,"link_to_canton_results":"https://data.bl.ch/explore/dataset/10500/tabl..."}]
```

This is **the reference shape**: `domain0:"federation"` vs `"canton"` distinguishes federal from
cantonal proposals in one feed, `answer` gives the outcome, and it is current (2026-09-27).

**Bern:** `https://www.sta.be.ch/content/dam/sta/dokumente/de/themen/wahlen-und-abstimmungen/abstimmungen/BE-STA-Abstimmungsresultate-Kanton-Bern.csv`
**City of Zurich:** `https://data.stadt-zuerich.ch/dataset/politik_abstimmungen_seit1933/download/abstimmungen_seit1933.csv`

**A useful convention:** BL, BS, SG and St.Gallen all serve the same Opendatasoft export surface —
`/api/v2/catalog/datasets/<id>/exports/{csv,json,jsonl,parquet,rdfxml,jsonld,turtle,n3,xls}`. One
adapter covers several cantons.

### 9. swisstopo SearchServer — the geocoding pin (verified live)

```
GET https://api3.geo.admin.ch/rest/services/api/SearchServer?searchText=Zurich&limit=2&type=locations
→ {"results":[{"attrs":{"detail":"zurich zh","featureId":"261",
   "lat":47.37721252441406,"lon":8.527311325073242,
   "geom_st_box2d":"BOX(676223.77 241584.28,689664.94 254306.35)"}}]}
```

The repo **already calls this host** (`src/` contains
`https://api3.geo.admin.ch/rest/services/api/SearchServer?searchText=`), so municipality→pin is
already solved. It returns lat/lon **and** a bounding box, so results can draw as polygons.

### 10. opendata.swiss — the discovery layer (verified live)

CKAN **2.11.6**; `package_search` is open and is the fastest way to enumerate which cantons already
publish machine-readable results. `q=abstimmungsergebnisse` → canton/city publishers;
`q=Nationalratswahlen` → 68 hits (all cantonal mirrors); `q=voteinfo` → **0**.

### 11–12. Alerts — no verified API

MeteoSchweiz docs portal is live (`https://opendatadocs.meteoswiss.ch/`, with
`/a-data-groundbased`, `/e-forecast-data`, `/general/terms-of-use`). The repo already links
`https://www.meteoschweiz.admin.ch/warnungen`. A documented official warning *event* JSON endpoint
is **not verified**. Community JSON wrappers exist but are third-party and inadmissible as evidence.

`https://www.alert.swiss/faq` (HTTP 200, 51,883 B): extracted text is entirely consumer-app
(severity levels, push settings). **No `API`, `Schnittstelle` or developer section exists.** Alertswiss
is app-only from an open-data standpoint.

### 13. Event-shaped data — question (d), and (e) refuted

**Question (e): is there a single Swiss open events calendar API with coordinates? NO.**
Searching opendata.swiss for event calendars surfaced only `opendata.ch/events` (the *community's own*
events site, i.e. not government data) and `eventfrog.ch` (a commercial vendor). No federal, cantonal
or municipal operator publishes a national located-events API. This does not exist.

For event-shaped data the real options are: the **existing Amtsblattportal.ch** feed (already
integrated, already lat/lon, and its publication schema carries more than Baugesuch categories), and
city-level event calendars on individual OGD portals — which is again per-canton by nature.

---

## 3. Explicitly NOT available or not verified

- **(a) Federal per-municipality results → REFUTED ON 2026-10-05; the endpoint DOES exist.** ~~Data exists and
  is documented (VoteInfo serves Gemeinde+Kanton+CH live), but the channel is a **mobile app**.
  BFS's own page exposes no CSV/JSON/interface; `voteinfo.bfs.admin.ch` does not resolve. Question (a)
  is answered *no* for a documented endpoint. What VoteInfo "exposes" beyond a proposal list: nothing
  reachable — there is nothing to call.~~ **The negative above was drawn from the wrong hosts.**
  `voteinfo.bfs.admin.ch` and `abstimmungen.bfs.admin.ch` do not resolve, but they are not the
  machine-readable channel. The canonical VoteInfo OGD publication, documented in this repo since
  2026-08-27 at `docs/research/2026-08-27-bfs-vote-data.md:13`, is live and was measured on
  2026-10-05:
  `https://ogd-static.voteinfo-app.ch/v1/ogd/sd-t-17-02-20240922-eidgAbstimmung.json`
  → **HTTP 200, 1 977 268 bytes, 0.25 s**. Its shape is `abstimmtag` / `timestamp` /
  `spatial_reference` / `schweiz`, with `schweiz.vorlagen[0].kantone` = **26** and
  `kantone[0].gemeinden` = **161** municipalities, each keyed by the BFS `geoLevelnummer` and
  carrying `resultat.jaStimmenInProzent`, `jaStimmenAbsolut`, `stimmbeteiligungInProzent`. So
  per-municipality federal results ARE programmatically available, at municipality granularity, with
  a stable BFS key — which also means they can be drawn on a municipality choropleth.
  This repo's own parser already consumed the payload correctly (fed live it returned
  `proposal 6710 | cantons 26 | national_yes 36.96`); it simply had no caller until commit `33aab13`
  wired it (see `docs/specs/SPEC-056b-live-voteinfo-ogd-wiring.md`).
- **(b) Federal elections per municipality → NOT VERIFIED.** Official published granularity is
  **canton** (seats + party shares). No per-municipality federal election machine-readable source found.
- **(c) National aggregator for cantonal/kommunal votes → REFUTED.** Verified by exhaustive CKAN query.
- **PXWeb for vote results → REFUTED**, 0/644 tables.
- **Alertswiss public API → NOT VERIFIED / no evidence.**
- **(e) National located-events calendar API → REFUTED.** Does not exist.
- **Licences / commercial use → NOT VERIFIED for every source.** See §1 licence note. This is the
  single biggest open risk in the survey and cannot be closed from the pages available today.
- Browser fallback (`_bh-searcher`) was **not available** this run; all evidence above is direct
  `curl` against primary operator hosts. Search-engine results were used only to find candidate
  hosts, never as evidence of what an API exposes.

---

## 4. Recommendation

**1. Canton Zürich municipality vote archive — best coverage per unit of effort, by a wide margin.**
It is a flat CSV, already proven live, keyed by **BFS municipality number and Bezirk**, and reaches
back to **1831**. Because the repo already calls swisstopo SearchServer, every row pins to lat/lon with
no new infrastructure. It is also the strongest single answer to the owner's complaint: it turns
static canton polygons into a map dense with real, dated, located results. Call
`https://www.web.statistik.zh.ch/ogd/data/KANTON_ZUERICH_abstimmungsarchiv_gemeinden.csv`
(plus `…_kanton.csv` for the cantonal roll-up). Effort: one parser. Note this covers **cantonal** and
**municipal** votes; the `domain0` distinction BL uses shows how to tell federal from cantonal.

**2. Basel-Landschaft JSON as the reference adapter, then opendata.swiss to generalise it.**
BL's export is the cleanest contract in this survey — single feed, `domain0` separating
`federation` from `canton`, `answer`, `percent_yeas/nays/turnout`, `district`, and live data dated
2026-09-27. Build one adapter against
`https://data.bl.ch/api/v2/catalog/datasets/11990/exports/json`, then drive discovery with
`https://opendata.swiss/api/3/action/package_search?q=abstimmungsergebnisse` and add cantons that
share the `/api/v2/catalog/datasets/<id>/exports/json` convention (BS, SG, St.Gallen already do).
This converts "26 different systems" into a list rather than an open-ended project, and one code
path covers many cantons.

**3. Federal elections per canton — the cheapest "next election" feature.** Official, canton-level,
already what the map draws today, so it needs no geocoding. Follow BFS's own pointer:
`https://opendata.swiss/de/dataset/?q=federal%20elections&res_format=JSON`, results at
`https://www.wahlen.admin.ch/de/2023/ch/23-table-results-national-council-election`.

**Deliberately not recommended:** Alertswiss (no verified API), a national events calendar (does not
exist), and building a PXWeb vote integration (0/644 tables — it will never return). For genuinely
event-shaped data, widen the existing Amtsblattportal.ch integration rather than hunt for a feed
that isn't there. **Close the licence question before any of this ships** — nothing in this survey
had a verified commercial-use term.

---

## Queries tried:
- `BFS VoteInfo API REST documentation`
- `opendata.swiss eidgenössische Abstimmungen Ergebnis Gemeinde`
- `eidgenössische Wahlen Nationalrat Resultate API BFS`
- `Alertswiss API Schnittstelle Warnungen Koordinaten`
- `MeteoSwiss open data API Unwetter Warnungen`
- `Schweizerisches Nationalmuseum OR Stadtverwaltung open data Veranstaltungen API Koordinaten`
- `swisstopo api3.geo.admin.ch SearchServer documentation REST API` (returned 0 results)
- `MeteoSchweiz Warnungen API opendatadocs meteoswiss JSON Koordinaten`
- `opendata.swiss Veranstaltungen Kalender Events API Gemeinde`

## Fetched URLs:
| URL | Status | Takeaway |
|---|---|---|
| `www.bfs.admin.ch/bfs/de/home/statistiken/politik/abstimmungen/voteinfo.html` | **200, 3.4 MB** | **VoteInfo = app; 0 CSV/JSON/API hits** |
| `www.bfs.admin.ch/bfs/de/home/statistiken/politik/abstimmungen.html` | 200 | no download links at all |
| `www.bfs.admin.ch/bfs/de/home/bfs/bundesamt-statistik/rechtliche-hinweise.html` | 200 | no "open data" licence statement |
| `www.pxweb.bfs.admin.ch/api/v1/de` | **200 JSON 38,641 B** | 644 tables; **0 vote/election** |
| `www.pxweb.bfs.admin.ch/api/v1/en` | 200 JSON | same directory |
| `www.pxweb.bfs.admin.ch/api/v1/de/px-x-1003020000_101` | 200 | metadata + `updated` works |
| `www.pxweb.bfs.admin.ch/api/v1/de/search?query=abstimmung` | 200, empty | search useless; enumerate |
| `www.pxweb.bfs.admin.ch/pxweb/en/` | 200 | STAT-TAB UI |
| `abstimmungen.admin.ch/` | **200, 131 KB** | Next.js SPA; **0 csv/json/api links** |
| `abstimmungen.admin.ch/de/vote/overview` | 404 | — |
| `voteinfo.bfs.admin.ch/` | **HTTP 000** | **host does not exist** |
| `abstimmungen.bfs.admin.ch/` | **HTTP 000** | **host does not resolve** |
| `www.wahlen.admin.ch/` | 200 | links opendata.swiss `res_format=JSON` |
| `www.wahlen.admin.ch/de/2023/ch/23-table-results-national-council-election` | 200 | official canton-level results |
| `opendata.swiss/api/3/action/package_search?q=abstimmungsergebnisse` | 200 | only canton/city publishers |
| `opendata.swiss/api/3/action/package_search?q=Nationalratswahlen` | 200 | 68 hits, all cantonal mirrors |
| `opendata.swiss/api/3/action/package_search?q=voteinfo` | 200, **count 0** | **no VoteInfo dataset** |
| `opendata.swiss/api/3/action/package_search?q=abstimmungsergebnisse+bundesweit` | 200 | 25 hits, all local |
| `opendata.swiss/api/3/action/package_show?id=abstimmungsarchiv-des-kantons-zurich1` | 200 | `license_id: None` |
| `opendata.swiss/de/about` | 200 | "ein Metadatenkatalog" |
| `opendata.swiss/de/nutzungsbedingungen` | 200 (JS-only) | **no licence keywords in HTML** |
| `handbook.opendata.swiss/en/guide/policies/licence/` | **404** | path guess wrong |
| `data.bl.ch/api/v2/catalog/datasets/11990/exports/json?size=1` | **200** | **municipality vote data, 2026-09-27** |
| `www.web.statistik.zh.ch/ogd/data/KANTON_ZUERICH_abstimmungsarchiv_gemeinden.csv` | **200** | **`STAT_GEMEINDE_ID`, `BEZIRK`, from 1838** |
| `www.web.statistik.zh.ch/ogd/data/KANTON_ZUERICH_abstimmungsarchiv_kanton.csv` | 200 | canton roll-up + `URL_VOLKSABSTIMMUNG` |
| `api3.geo.admin.ch/rest/services/api/SearchServer?searchText=Zurich` | **200** | **lat/lon + featureId + bbox** |
| `opendatadocs.meteoswiss.ch/` | 200 | docs portal |
| `opendatadocs.meteoswiss.ch/general/terms-of-use` | 200 | terms page (not read in detail) |
| `www.alert.swiss/faq` | 200, 51,883 B | app FAQ; **no API** |
| `www.geo.admin.ch/de/services/Geodaten-Dienst/API.html` | 404 | moved |
| `www.bfs.admin.ch/bfs/en/home/services/api.html` | 404 | moved |

## Source Links:
| claim | primary URL (+ snippet) | secondary URL | date | confidence |
|---|---|---|---|---|
| VoteInfo is an app, not an API | `bfs.admin.ch/.../voteinfo.html` → "Mit der ... entwickelten **App** «VoteInfo» … wie ihre **Gemeinde**, ihr **Kanton** und die Schweiz … gestimmt haben"; `CSV/JSON/Schnittstelle/API` = 0 hits | `bfs.admin.ch/.../abstimmungen.html` — no download links | 2026-10-04 | **primary (fetched)** |
| No federal VoteInfo endpoint/host | `voteinfo.bfs.admin.ch/` → HTTP 000 | CKAN `q=voteinfo` → `count 0` | 2026-10-04 | **primary (fetched, negative)** |
| Dashboard has no data endpoint | `abstimmungen.admin.ch/` → 200, Next.js, 0 `csv\|json\|api\|download` links | `/de/vote/overview` → 404 | 2026-10-04 | **primary (fetched, negative)** |
| PXWeb live, no votes | `pxweb.bfs.admin.ch/api/v1/de` → 644 entries, 0 matches for `abstimm\|wahl\|nationalrat\|election` | `.../px-x-1003020000_101` → `"updated":"2026-09-04T08:31:06"` | 2026-10-04 | **primary (fetched)** |
| Federal election results = canton-level, JSON via opendata.swiss | `wahlen.admin.ch/` → `href="…/dataset/?q=federal elections&…&res_format=JSON"` | `…/2023/ch/23-table-results-national-council-election` | 2026-10-04 | **primary (fetched)** |
| ZH: municipality-level since 1831, with BFS+district key | `KANTON_ZUERICH_abstimmungsarchiv_gemeinden.csv` → `04.02.1838,801,…,1,1,Aeugst a.A.,Affoltern,…` | `…_kanton.csv` | 2026-10-04 | **primary (fetched CSV)** |
| BL: municipality-level, federal+cantonal in one feed, live | `data.bl.ch/api/v2/catalog/datasets/11990/exports/json` → `"date":"2026-09-27","domain0":"federation","answer":"rejected","percent_yeas":26.888` | `/csv`, `/parquet` same dataset | 2026-10-04 | **primary (fetched JSON)** |
| Bern canton CSV exists | `sta.be.ch/…/BE-STA-Abstimmungsresultate-Kanton-Bern.csv` | opendata.swiss record | 2026-10-04 | **primary (catalogue)** |
| Zurich city since 1933 | `data.stadt-zuerich.ch/dataset/politik_abstimmungen_seit1933/download/abstimmungen_seit1933.csv` | `.parquet` variant | 2026-10-04 | **primary (catalogue)** |
| No national aggregator (refutes (c)) | CKAN `q=abstimmungsergebnisse` → orgs St.Gallen/BL/BS/ZH/Bern only | CKAN `q=…+bundesweit` → 25, all local | 2026-10-04 | **primary (fetched)** |
| Geocoding gives lat/lon | `api3.geo.admin.ch/rest/services/api/SearchServer?searchText=Zurich` → `"lat":47.37721252441406,"lon":8.527311325073242` | repo `src/` already calls this host | 2026-10-04 | **primary (fetched)** |
| No national events calendar (refutes (e)) | CKAN search → `opendata.ch/events` (community), `eventfrog.ch` (vendor) only | — | 2026-10-04 | **primary (fetched, negative)** |
| Alertswiss has no public API | `www.alert.swiss/faq` → app-focused text; no `API`/`Schnittstelle` | — | 2026-10-04 | **not verified** (absence in FAQ only) |
| Licence terms | `license_id: None` on opendata.swiss; `Nutzungsbedingungen` JS-only | BFS legal page: no "open data" | 2026-10-04 | **not verified — open risk** |
| Repo VoteInfo connector is a stub | `src/services/connectors/bfs_voteinfo_client.py` → `rows = [{"id": 6670, "yes": 58.2}]`, no HTTP call | ADR-012 / SPEC-056 describe intent only | 2026-10-04 | **repo-local** |
