# Research — Planning pillér adatforrások: Amtsblattportal API + ÖREB M2M

- **Dátum:** 2026-08-26
- **Kérdés:** Milyen gépi kontraktum áll rendelkezésre a ZH Baugesuch-publikációkra és az ÖREB zónákra?
- **Módszer:** élő API-próbahívások (curl, 2026-08-26) + hivatalos dokok (amtsblattportal.ch/docs/api, cadastre-manual.admin.ch, Geolion ZH) + openZH/NachbR referencia-implementáció
- **Kanban:** t_add5150f

## 1. Amtsblattportal API v1 — ÉLŐEN IGAZOLT ✅

Base URL: `https://amtsblattportal.ch/api/v1/publications/xml`

| Paraméter | Érték | Megjegyzés |
|---|---|---|
| `publicationStates` | `PUBLISHED` | **kötelező** |
| `cantons` | `ZH` | többször is megadható (`&cantons=BE`) |
| `rubrics` | `BP-ZH` | Baupublikationen ZH |
| `subRubrics` | `BP-ZH01` | Baugesuch altípus |
| `publicationDate.start/end` | `YYYY-MM-DD` | dátumszűrő — élően tesztelve |
| `pageRequest.size` | pl. `100` | lapozás |

**Élő bizonyíték (2026-08-26):**
- Szűretlen BP-ZH: `<total>6669</total>`
- Utolsó 7 nap (`2026-08-20→08-26`): `<total>120</total>` → ~17 publikáció/nap
- `/json` **lista** végpont NEM létezik (`PUBLICATION.EXCEPTION.NOT FOUND`) → **XML a kontraktum**

**Mezők (XML, kabzh `BP-ZH01-export.xsd`):** `id` (UUID), `title.de`, `registrationOffice.{swissZipCode,town,municipalityId,displayName}`, `publicationNumber`, `publicationState`, `publicationDate`, `expirationDate` (publikáció +1 év!), `legalRemedy` (szöveg, benne az Auflage/Einsprache szabály), `cantons`.

### Válaszok a terv 4 döntési kérdésére

1. **Koordináta:** ❌ NINCS gépi koordináta a meta-ban → geokódolás kell (cím a title-ben: pl. „Seefeldstrasse 6, … Uster"; Swisstopo `type=locations` már integrált). Kompromisszum: cím-szintű pont, fallback községközéppont — dokumentálandó a rekordon (`geocode_precision` mező).
2. **Polling gyakoriság:** **napi 1 elég** (a portál és az OGD dataset is napi frissítésű; mi is ~17 új rekord/napot várunk).
3. **Tárolás:** MVP **SQLite** (`baugesuche` tábla, TTL: `expiration_date` oszlop + `is_active` számítás) — PostGIS később, külön ADR.
4. **Jogi:** csak publikus Auflage-adatok; **minden rekordban `source_url`** = `https://amtsblattportal.ch/api/v1/publications/{id}/xml` (vagy HTML megfelelője).

⚠️ **Auflage-ablak nuansz:** a portál `expirationDate`-e ~1 év (láthatósági TTL), NEM a jogi Auflage-friss. Az `legalRemedy` szövegből: a Planauflage friss ideje (~20 nap a publikációtól) nem gépi mező. MVP-döntés: `auflage_start = publicationDate`, `auflage_end = publicationDate + 20 nap` (konfigurálható `AUFLAGE_DAYS`), a láthatósági TTL külön mezőben. Közelítés — dokumentálva.

## 2. OGD dataset 2982 (Statistisches Amt ZH) — kiegészítő forrás

- „Baugesuche im Kanton Zürich" (`2982@statistisches-amt-kanton-zuerich`, opendata.swiss): **összes Baugesuch 2024 őse óta, napi automatikus frissítéssel**, JSON/XML letöltés.
- Referencia-implementáció: [openZH/NachbR](https://github.com/openZH/baupub) (R) — ugyanezt az API-t hívja `rubrics=BP-ZH&subRubrics=BP-ZH01` paraméterkészlettel → kontraktum-univerzum igazolva harmadik fél által is.
- Hasznos: történeti backfill (a portál ~1 évre fogadja el régi rekordok lekérését).

## 3. ÖREB M2M — magas komplexitás, elhalasztva

- Szövetségi keret: DATA-Extract (**XML kötelező**, JSON opcionális) + ÖREB-Webservice kantononként (cadastre-manual.admin.ch Weisungen).
- ZH: `https://maps.zh.ch/oereb` (GIS-Browser), WFS: `https://maps.zh.ch/wfs/OerebKatasterZHWFS` (Geolion 2029; Nutzungsplanung/Baulinien/GW/KbS rétegek).
- Értékelés: valódi érték (zónainfo a térképre), de parcella-szintű extract + Interlis/XML feldolgozás külön kutatási ciklust igényel → **Task 5 / külön ADR-003**, nem ebben a ciklusban (audit C-vel konzisztens).

## 4. Comparison table — implementációs opciók (1–5)

| Kritérium | **A: Élő Amtsblatt XML ETL** (napi poll) | **B: OGD 2982 batch** (napi fájlletöltés) | **C: ÖREB M2M most** |
|---|---|---|---|
| Érték (frissesség, kontroll) | 5 | 4 | 5 |
| Költség (implementáció olcsósága) | 3 | 5 | 1 |
| Kockázat (stabilitás, kontraktum-garancia) | 3 | 4 | 2 |
| Karbantarthatóság | 4 | 4 | 2 |
| **Összesen** | **15** | **17** | **10** |

**Meglepő eredmény:** B (OGD batch) önmagában a legegyszerűbb, DE a terv architektúrája (élő áramló feed, saját TTL-logika) és a verseny-tanulság (20 napos ablak) miatt **A+B hibrid a javaslat**: A adja az élő napi incrementet és a jogi meta-mezőket, B (későbbi kártya) a 2024 óta történeti backfillt. C elvetve ebben a ciklusban.

## Források
- https://www.amtsblattportal.ch/docs/api/ (hivatalos REST dok)
- https://opendata.swiss/de/dataset/baugesuche-im-kanton-zurich (2982 dataset)
- https://github.com/openZH/baupub (NachbR toolkit)
- https://www.cadastre-manual.admin.ch/de/m2m-oereb-katasterauszug (DATA-Extract)
- https://geolion.zh.ch/geodatenservice/2029 (ZH ÖREB WFS)

→ Javaslat az ADR-002-be: **ADR-002-data-ingestion-pipeline.md**

## Független újravalidáció (2026-08-26, 2. futás — friss curl-bizonyítékok)

- Heti lista (`BP-ZH`+`BP-ZH01`, `2026-08-20→08-26`) újrahívva: `<total>120</total>` ✅ (~17/nap megerősítve).
- `/json` **lista** → HTTP 404 `PUBLICATION.EXCEPTION.NOT.FOUND`; `/json` **single** → HTTP 404. Az XML-only kontraktum újra igazolva.
- Élő single publikáció (Uster, `c1f797ae-…`): minden állított mező jelen (`registrationOffice.swissZipCode/town/municipalityId`, `publicationDate=2026-08-26`, `expirationDate=2027-08-26` = +1 év, `legalRemedy` Auflage-szöveggel); **nincs koordináta**, cím a `title.de`-ben („Seefeldstrasse 6, Assek. Nr. 7325, Uster").
- ⚠️ Új megfigyelés — **schema-verzió drift**: a dok oldal „latest PROD 1.24"-et mond, az élő XML `xsi:schemaLocation` viszont `…/schemas/kabzh/1.26/BP-ZH01-export.xsd`-re mutat. A névtér verziózott → a parser legyen **verzió-toleráns** (ne a verziószámra, hanem a helyi nevekre szűrjön).
