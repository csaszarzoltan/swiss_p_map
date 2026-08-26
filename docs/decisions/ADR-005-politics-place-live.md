# ADR-005: Politics + Place élő adatok — PARIS + ARE/BAFU/GWR hibrid (ZH pilot)

- **Dátum:** 2026-08-26
- **Státusz:** accepted (2026-08-26 — programozott folytatás, ADR-004-gyel együtt)
- **Szerző:** analyst (research: `docs/research/2026-08-26-politics-live-sources.md`, `...-place-live-sources.md`)
- **Kanban:** Politics+Place live (ADR-002 planning után)

## Kontextus

`place_service.py` 8004/8001 stub (119%), `politics_service.py` 8004/8001 stub. Cél: élő scrapelt/OGD adatok 4 nyelven, postcode-felbontással. Place-ra nincs egy nemzeti CSV mind a 4-re; Politics-ra PARIS XML CQL + parlament OData + Lobbywatch ZIP.

## Döntés

**Place hibrid B primary (4.6/5 nyert):** `geo.admin.ch api3 Identify` (LV95 pont-lekérdezés) + WMS overlay

- `steuerfuss_percent`: OGD ZH `data.stadt-zuerich.ch` CSV → BFS-Nr→PLZ join; fallback BL-minta
- `noise_db_day`: `api3 Identify ch.bafu.larm-strassenlaerm_tag @LV95` → dB sávközép + WMS `ch.bafu.larm-*` overlay (10×10m raster, 2015 modell 2021 counts, BAFU disclaimer)
- `oev_class`: `api3 Identify ch.are.gueteklassen_oev @LV95` → A–D/none (ARE 2025-03, GTFS jährlich)
- `gwr_building_count`: `WFS ch.bfs.gebaeude_wohnungs_register?bbox=PLZ` (Datenstand 2026-07-12) / BS daily CSV fallback

**Politics A primary (21/25):** PARIS-API direkt (`gemeinderat-zuerich.ch/api`, XML CQL, 23 index, Wahlkreis mező, near-realtime, `postcode→Wahlkreis` JSON lookup 8001→1+2, 8004→4+5) + secondary `ws.parlament.ch OData` (Nationalrat Business/Vote JSON, postcode→Kanton) + tertiary batch `lobbywatch ZIP heti` + `Abstimmungen CSV` (opendata.swiss) — Kantonsrat scraping elhalasztva

## Elvetve

| Opció | Miért nem |
|---|---|
| Place A: opendata.swiss CSV only | csak TG/BL/ZG, ZH-ra nem vetíthető; Lärm/ÖV nincs CSV |
| Place C: hard scrape BFS/BAFU/ARE | HTML-törékeny, nincs SLA, IP-ban |
| Politics B: CKAN CSV only | csak Abstimmungen, nincs Vorstoss, napok késés |
| Politics C: Lobbywatch+Kantonsrat scrape | heti ZIP ok de scraping törékeny + ToS |

## Következmény

- Kártyák: `feat: Place OGD kliensek (ZH-CSV + BAFU/ARE Identify + GWR WFS)` → Protocol-DI `place_service.py` stub csere; `feat: Politics live (PARIS CQL + parlament OData)` → `politics_service.py`; mind `httpx`+mock tesztek, `source_url` kötelező, max 400 sor/file
- Validálás: 8004 Langstrasse Identify próba (ÖV=A, Lärm>60, GWR>3000) + PARIS `Wahlkreis any "4"` ≥2 hit + Lobbywatch ZIP 200

## Kapcsolódó

- Research: `docs/research/2026-08-26-{place,politics}-live-sources.md`
- Kód: `src/services/place_service.py`, `src/services/politics_service.py`, `src/models/place.py`
- Következő: RED→GREEN az ADR-ek szerint (minden új funkció research-módszertannal)
