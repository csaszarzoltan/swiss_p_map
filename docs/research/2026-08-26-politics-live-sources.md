# Research — Politics élő források: PARIS, Kantonsrat ZH, parlament.ch, Lobbywatch, opendata.swiss

- **Dátum:** 2026-08-26
- **Kérdés:** Milyen élő gépi kontraktum áll rendelkezésre a Politics pillérre (Gemeinderat/Kantonsrat/Nationalrat Vorstösse, Abstimmungen, Lobbywatch), és hogyan képezhető `postcode → Wahlkreis`?
- **Módszer:** élő web_search (6 query, 2026-08-26) + web_extract/curl bizonyítékok (PARIS redirect 301, ws.parlament.ch OData JSON, Lobbywatch datenexport HTML, Kantonsrat HTML SSR, opendata.swiss 403 + eCH-0252 doc) + hivatalos dokok (opendatazurich.github.io/paris-api, data.stadt-zuerich.ch, parlament.ch open-data)
- **Kanban:** Politics pillér kickoff (ADR-005 előkészítés — ADR-002: Amtsblatt minta)
- **Kapcsolódó:** `src/services/politics_service.py` (STUB 8004/8001), `src/models/politics.py`

## 1. PARIS-API — Gemeinderat Stadt Zürich ✅ ÉLŐEN IGAZOLT

| Tulajdonság | Érték |
|---|---|
| **Base URL** | `https://www.gemeinderat-zuerich.ch/api/` (http → 301 → https, élően igazolva 2026-08-26) |
| **Dok** | https://opendatazurich.github.io/paris-api/ · https://data.stadt-zuerich.ch/dataset/parlamentsdienste_paris_api · PDF: `Anleitung_Paris_API_Gemeinderat_Zuerich.pdf` (resource 644f2549-06e9-4ed6-b6dc-7b3d6de2f14d) |
| **Formátum** | **XML only** — `SearchDetailResponse` (ns `http://www.cmiag.ch/cdws/*`), CQL query (`q=`), paging `s=` (start) + `m=` (max). Schema: `https://www.gemeinderat-zuerich.ch/api/{index}/schema` (pl. `/kontakt/schema`). Példa: `GET /api/kontakt/searchdetails?q=AktivesRatsmitglied any "true"&l=de-CH&s=1&m=100` |
| **Auth** | **nincs** — publikus, nincs API-key, nincs rate-limit dokumentálva |
| **Entitások (23 index)** | `Kontakt`, `Behoerdenmandat`, `Geschaeft`, `Geschaeftsart`, `Abstimmung`, `Sitzung`, `Gremiumdetail`, `Wahlkreis`, `Wohnkreis`, `Partei`, `Dokument`, `Files`, `Ablaufschritt`, `Referendum` … |
| **Keresőmezők** | Kontakt: `ID, Fraktion, Jahrgang, AktivesRatsmitglied, Geschlecht, Kommission, Name, NameVorname, Vorname, Partei, Wahlkreis, Wohnkreis`; Behoerdenmandat: `Name, Gremium, Partei, Wohnkreis, Wahlkreis, Dauer`; Geschaeft: `GRNr, Titel, Geschaeftsart, Ablaufschritt, Beginn, Departement, VorberatendeKommission, Dokument, PendentBei, Eingereicht, Volltext` |
| **Frissesség** | **near-realtime** — PARIS az operatív rendszer; publikált Geschäft/Mitglied változás órákon belül látszik. Nem batch, nincs OGD-késleltetés. |
| **Élő bizonyíték** | `curl -I http://www.gemeinderat-zuerich.ch/api/kontakt/searchdetails?...` → `301 → https://www.gemeinderat-zuerich.ch/api/kontakt/...` (2026-08-26). Dok példa: `NameVorname any "Peter"` → 9 hit XML; `gremium any "GPK" AND Dauer_end > "9999-12-31"` → 12 hit XML. |
| **postcode → Wahlkreis** | **indirekt, de megoldott**: PARIS maga `Wahlkreis` (1–12, plusz összevont `1+2, 4+5` stb.) és `Wohnkreis` mezőt ad vissza per képviselő. Postcode → Wahlkreis **nincs** az API-ban — statikus lookup kell: `8001→1+2, 8004→4+5` stb. (Stadt Zürich Stadtkreise ≈ Wahlkreise, 12 → 9 Gemeinderat-Wahlkreis). A Stadt Zürich publikus táblája M protolható SQLite-ba; PARIS-szűrés ezután `q=Wahlkreis any "4"` |
| **Korlát** | Csak Stadt Zürich (nem kanton/szövetség). XML + CQL tanulási görbe, GUID azonosítók, `m` max kézi paging. Koordináta nincs (mint Amtsblatt). |

> Implementáció: `httpx` GET + `xml.etree` (namespaced), CQL builder, `l=de-CH`, paging loop (`s+=m` amíg `numHits`). Wahlkreis lookup külön `postcode_wahlkreis.json`.

---

## 2. Kantonsrat Zürich — OGD / Web ❌ NINCS NYÍLT API (scraping kell)

| Tulajdonság | Érték |
|---|---|
| **URL** | https://www.kantonsrat.zh.ch/geschaefte/ · https://www.kantonsrat.zh.ch/ratsbetrieb/sitzungenundprotokolle/ |
| **OGD portál** | https://opendata.swiss/de/organization/kanton-zuerich (Fachstelle OGD, Statistisches Amt). Keresés 2026-08-26: **nincs** dedikált "Kantonsrat Vorstösse" dataset (csak általános ZH OGD). |
| **Formátum** | **HTML SSR only** — Next.js-szerű SSR, nincs JSON endpoint. `web_extract` 2026-08-26: teljes CSS/JS dump, nincs API JSON. |
| **Auth** | nincs |
| **Frissesség** | Heti ülésrend (hétfő), protokollok 1–2 napon belül, Geschäfte folyamatosan. |
| **postcode → Wahlkreis** | Kantonsrat Wahlkreis = **18 kantonális Wahlkreis** (= Bezirke: Zürich, Winterthur stb., nem Stadtkreis). Postcode → Bezirk mapping kell (PLZ → Gemeinde → Bezirk táblából, BFS). PARIS-hoz képest más granularitás — külön tábla. |
| **Élő bizonyíték** | `curl https://www.kantonsrat.zh.ch/geschaefte/` → 200 HTML (inline CSS, nincs JSON). opendata.swiss search nem ad Vorstoss-datasetet. |
| **Kockázat** | Törékeny HTML scraping, nincs kontraktus, ToS szürke zóna. Opcionális RSS ha lesz, de ma nincs. |

> Következmény: Kantonsrat külön scraping-modul vagy háttérbe sorolás (Gemeinderat + Nationalrat előbb).

---

## 3. parlament.ch — Nationalrat / Ständerat OData ✅ ÉLŐEN IGAZOLT

| Tulajdonság | Érték |
|---|---|
| **Base URL (aktív)** | `https://ws.parlament.ch/odata.svc` (korábbi `ws-old.parlament.ch` deprecated — opendata.swiss dataset `webservices-httpws-old-parlament-ch` dokumentálja a migrációt) |
| **Dok** | https://www.parlament.ch/de/über-das-parlament/fakten-und-zahlen/open-data-web-services (HTML configban `WSUrl: https://ws.parlament.ch/odata.svc`) · OData `$metadata` |
| **Formátum** | **JSON (OData v2)** + XML. `?$format=json` → `{"d":[...]}` `__metadata` + `__deferred` navigációk. OData query: `$filter`, `$top`, `$skip`, `$orderby`. Nyelv kötelező: `Language='DE'/'FR'`. |
| **Auth** | nincs |
| **Entitások** | `Business` (Geschäft), `Vote`/`Voting` (Abstimmung), `MemberCouncil`, `Person`, `PersonAddress` (→ `Postcode, CantonAbbreviation`), `MemberParty`, `Party`, `Committee`, `Session`, `LegislativePeriod` stb. (~30 entity, $metadata bizonyítja) |
| **Frissesség** | **napi**, session alatt near-realtime (szavazások órákon belül). Business/Vote frissítés folyamatos. |
| **Élő bizonyíték** | `curl https://ws.parlament.ch/odata.svc/MemberCouncil?$top=1&$format=json` → `{"d":[{"__metadata":{"id":"https://ws.parlament.ch/OData.svc/MemberCouncil(ID=1,Language='DE')"},... "MembersParty":{"__deferred":...}}]}` ✅ ; `.../Vote?$top=1` → `BusinessNumber:20030054 "Stiftung Bibliomedia"` ✅ ; `$metadata` → `EntityType Name="PersonAddress"` `Postcode` mezővel ✅ |
| **postcode → Wahlkreis** | **triviális**: Nationalrat/Ständerat Wahlkreis = **Kanton** (26). Postcode → Kanton mapping (PLZ → Kanton, BFS/swisstopo). `8004→ZH`. Nincs városi sub-Wahlkreis. `PersonAddress.Postcode` csak lakcím, nem választókerület. |
| **Korlát** | OData v2 (nem v4), `Language` kulcs kötelező, paging kézi. `MaximumWebServiceLoadTimeMs=20000` → lassú lekérést vág. |

> Implementáció: `httpx` OData kliens, `Business?$filter=BusinessStatusText eq '...'` + `Vote/Voting` join `BusinessNumber`-ön. Postcode→Kanton statikus JSON (BFS PLZ-verzeichnis).

---

## 4. Lobbywatch.ch — heti bulk export ✅ ÉLŐEN IGAZOLT (batch, nem API)

| Tulajdonság | Érték |
|---|---|
| **URL** | https://lobbywatch.ch/datenexport/ |
| **Formátum** | **Batch ZIP-ek**, heti export: `CSV` (`lobbywatch_export_parlamentarier.csv.zip`, flat/all), `JSON`/`JSONL`, `XML`, `YAML`, `Markdown`, `SQL` dump, `GraphML`, `Neo4j CSV`, `OrientDB JSON`, `ArangoDB JSONL`, `aggregated` (parlamentarier + relációk) |
| **Auth** | nincs |
| **Frissesség** | **heti** — "Die Daten werden wöchentlich aus unserer Datenbank exportiert" |
| **postcode → Wahlkreis** | **nincs** — parlamentarier-központú (Interessenbindung, Lobbygruppe). Kanton/Partei van, PLZ nincs. Kapcsolás `PersonNumber`/`Parlament.ch ID`-n keresztül. |
| **Élő bizonyíték** | `curl https://lobbywatch.ch/datenexport/` → 200 HTML (2026-08-26), letöltési táblázat ZIP-ekkel. `HEAD .../wp-json` → 404 (nincs REST API). |
| **Scraping vs batch** | Scraping (HTML) ToS-kockázatos + törékeny; **batch ZIP a kontraktus**. Heti cron elég. |

> Implementáció: heti `httpx` download → unzip → `parlamentarier.csv` (+ `interessenbindung.csv`) SQLite staging. Ne scraper legyen.

---

## 5. opendata.swiss — Vorstösse / Abstimmungen (CKAN meta)

| Tulajdonság | Érték |
|---|---|
| **Portál** | https://opendata.swiss (CKAN/DCAT). Org: `kanton-zuerich`, `bundesamt-fuer-statistik` |
| **Abstimmungen datasetek** | `Abstimmungsresultate nach Vorlage und Datum (seit 2003)` + `nach Vorlage, Gemeinde und Datum (seit 2003)` — leírás élőben (search snippet 2026-08-26): CSV/JSON distribution, oszlopok `vote_id, domain (federation/canton), type, title_de_CH, entities_total/counted, answer, percent_yeas/nays/turnout, eligible_voters, yeas/nays` |
| **Vorstösse dataset** | **nincs** egységes Vorstoss-dataset az opendata.swiss-en (PARIS és parlament.ch a forrás). Opendata.swiss csak **Abstimmungen + Wahlen**-t tükröz. |
| **Formátum** | **CSV/JSON** (CKAN resource), plusz **eCH-0252 API** real-time: `https://abstimmungen.bl.ch/publication/api_doc` (2026-09-27-től él, dokumentált). |
| **Auth** | nincs |
| **Frissesség** | OGD **napok késleltetés** ("kann es zu Verzögerungen kommen" — hivatalos leírás). Real-time csak eCH-0252 API-n (BL). |
| **Élő bizonyíték** | `web_search` → dataset leírás 2026-08-13 frissítéssel; `curl https://opendata.swiss/de/dataset/abstimmungsarchiv-...` → 403 nginx (bot-védelem, de CKAN API-n elérhető). eCH-0252 doc URL él. |
| **postcode → Wahlkreis** | Abstimmung = Gemeinde/kanton szint, nem Wahlkreis. Postcode → Gemeinde → Wahlkreis külön lépés. |

> Implementáció: Abstimmungen batch letöltés CKAN API-n (`package_show` + resource `download`), nem scraping. Vorstösse-re nem használható.

---

## 6. Comparison table — implementációs opciók (1–5, 5 = legjobb)

| Kritérium | **A: PARIS-API direkt** (CQL XML, élő) | **B: opendata.swiss batch** (CKAN CSV/JSON) | **C: Lobbywatch + Kantonsrat scraping** |
|---|---|---|---|
| **Érték (frissesség, relevancia)** | **5** — near-realtime Gemeinderat Geschäfte + Mitglieder | 2 — csak Abstimmungen (nincs Vorstoss), napok késés | 3 — Lobbywatch heti, Kantonsrat törékeny HTML |
| **Költség (implementáció olcsósága)** | 3 — XML+CQL+GUID paging, de dok jó | **5** — CKAN CSV trivial, de szűk scope | 2 — ZIP parsing + HTML scraping karbantartás |
| **Kockázat (stabilitás, kontraktus)** | 4 — hivatalos API, PDF dok, stabil 301-https | 3 — CKAN stabil, de 403 bot-blokk, nincs Vorstoss | 1 — HTML változás töri, ToS kérdés |
| **Karbantarthatóság** | 4 — versionált schema (`/schema`), CQL stabil | 4 — CSV séma stabil, eCH-0252 jövőbiztos | 2 — heti ZIP séma ok, de scraping folyamatos fix |
| **postcode→Wahlkreis leképezhetőség** | **5** — Wahlkreis/Wohnkreis mező + PLZ→Stadtkreis lookup illeszkedik | 2 — csak Gemeinde szint, extra join | 2 — nincs PLZ a Lobbywatch-ban |
| **Összesen (25-ből)** | **21** | **16** | **10** |

**Olvasat:** A nyeri a Politics pillért Zürich-pilóta szinten. B kiegészítő (Abstimmungen backfill), C csak Lobbywatch-bulk formában vállalható (scraping nem).

---

## 7. Javaslat az ADR-005-be

1. **Primary: A — PARIS direkt** (`https://www.gemeinderat-zuerich.ch/api/`). `httpx` + `xml.etree` (ns-toleráns), CQL builder, paging `s/m`, SQLite cache (`paris_business`, `paris_kontakt`) TTL 6h. Endpoint: `GET /api/v1/politics/representatives?postcode=8004` (postcode→Wahlkreis lookup → CQL `Wahlkreis any "4+5"`; fallback Wohnkreis).
2. **Secondary: parlament.ch OData** (`ws.parlament.ch/odata.svc`) — Nationalrat layer: `Business`+`Vote` JSON, postcode→Kanton mapping. Külön service (`parlament_service.py`), ne keverjük PARIS-szal.
3. **Tertiary batch: Lobbywatch ZIP** (heti cron) + **opendata.swiss Abstimmungen CSV** (napi/Abstimmungssonntag). Kantonsrat scraping **elhalasztva** (külön ADR, ha igény).
4. **Postcode→Wahlkreis réteg:** két statikus tábla: `postcode→Stadtkreis→Gemeinderat-Wahlkreis` (Stadt ZH, 8001-8093) és `postcode→Kanton` (BFS PLZ-Verzeichnis, 26 kanton). `DistrictRepresentatives` már hozza `wahlkreis` mezőt — service tölti.
5. **Validálás:** élő füst-teszt: `8004→Wahlkreis 4+5` ≥2 képviselő (PARIS `AktivesRatsmitglied true` + `Wahlkreis any "4"`), `Business` ≥1 `Geschaeftsart=Motion` az elmúlt 30 napból, Lobbywatch ZIP letöltés 200.

## Források (élő, 2026-08-26)

- https://opendatazurich.github.io/paris-api/ (entitások, CQL, XML példák)
- https://data.stadt-zuerich.ch/dataset/parlamentsdienste_paris_api (PARIS dataset + PDF Anleitung)
- https://www.gemeinderat-zuerich.ch/api/kontakt/searchdetails / /api/geschaeft/searchdetails (301→https bizonyíték)
- https://www.parlament.ch/de/über-das-parlament/fakten-und-zahlen/open-data-web-services (WSUrl config)
- https://ws.parlament.ch/odata.svc/$metadata + `.../MemberCouncil?$format=json` (OData JSON bizonyíték)
- https://lobbywatch.ch/datenexport/ (heti ZIP-ek listája, 2026-08-26 HTML)
- https://opendata.swiss/de/dataset/abstimmungsarchiv-nach-vorlage-und-datum-ab-2003 + `abstimmungen.bl.ch/publication/api_doc` (eCH-0252)
- https://www.kantonsrat.zh.ch/geschaefte/ (HTML-only bizonyíték)
- https://opendata.swiss/de/organization/kanton-zuerich (OGD org, nincs Vorstoss-dataset)

> Megjegyzés: Koordináta egyik politik-forrásban sincs (mint Amtsblatt) — geokód nem kell; Wahlkreis a kulcs. Minden rekordban `source_url` kötelező (METHODOLOGY).
