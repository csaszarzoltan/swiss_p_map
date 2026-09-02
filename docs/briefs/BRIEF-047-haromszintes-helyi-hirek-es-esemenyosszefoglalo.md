# BRIEF-047: 3 Szintes Helyi Hírek és Eseményösszefoglaló Modell

**Státusz:** READY_FOR_SPEC  
**Kapcsolódó feature:** FEAT-047  
**Forrás:** OpenBorough Local News & Today's Briefing mintája, a tényalapú újságírás és a 2026-09-02-i egyeztetés alapján

## Probléma

A hagyományos híroldalak végtelen, reklámokkal terhelt médiafolyamot kínálnak, ahol a felhasználónak nehéz kihámozni a konkrét helyi hatásokat (pl. érinti-e a zsebét, az építési szabályait vagy a lakókörzetét). Továbbá a generatív AI rendszereknél fennáll a hallucináció veszélye, ha nincsenek szigorú forrásmegkötések.

## Célcsoport és kontextus

Minden helyi polgár és vállalkozó, aki sallangmentes, strukturált és ellenőrzött forrású híreket szeretne kapni a kantonjáról és településéről.

## Kívánt eredmény

Egy **3 rétegű tényszerű hír- és eseménystruktúra**:
1. **1. szint: Mi történt?** — Tényszerű összefoglaló: esemény, dátum, érintett terület, hivatalos kiadó és ellenőrzött médiaforrások (pl. NZZ, Tages-Anzeiger, SRF, kantonális közlemény).
2. **2. szint: Miért fontos nekem?** — Helyi relevancia: adóváltozás, közlekedési fennakadás, helyi rendelet, építési övezet vagy mentett figyelési zóna érintettség.
3. **3. szint: Mi következik?** — Következő konkrét lépés: közmeghallgatási határidő, szavazási dátum, észrevételezési határidő vagy várható hivatalos döntés.

### Szigorú Forrás- és Biztonsági Szabályok:
- Minden hírhez kötelező metaadatok: Kiadó, publikálás időpontja, esemény tényleges dátuma, eredeti cikk URL, téma, besorolás (hivatalos közlemény, tényhír, véleménycikk, felmérés).
- **Anti-hallucinációs garancia:** A rendszer tilosban jár, ha kitalált híreket generál. Amennyiben egy élő kantonális RSS/hírforrás adapter még nem áll rendelkezésre, az állapot kötelezően `source_pending`.

## Jelenlegi / Tervezett funkciókat lefedő felhasználói történetek

- **US-047-01:** Helyi lakosként szeretném átfutni a lakóhelyem 3 legfontosabb friss hírét a "Mi történt / Miért fontos / Mi következik" 3 pontos szerkezetben.
- **US-047-02:** Felhasználóként egy kattintással az eredeti, hiteles hírforrásra akarok jutni.
- **US-047-03:** Felhasználóként szeretném, ha a rendszer azonnal figyelmeztetne, ha egy hír érinti a mentett figyelési zónámat (Watch Zone).

## Scope

- 3 szintes hír- és esemény-adatmodell.
- `GET /api/v1/news/local?postcode={postcode}` végpont.
- `LocalInformationHub.tsx` hírkártya adapter és `SourceTrustBadge` integráció.

## Non-scope

- Fizetős médiatartalmak (paywall) kikerülése vagy teljes szövegű kalóz újrapublikálása.

## Érintett rendszerek

- `src/services/local_information_service.py`, `frontend/src/components/LocalInformationHub.tsx`, `frontend/src/components/SourceTrustBadge.tsx`
