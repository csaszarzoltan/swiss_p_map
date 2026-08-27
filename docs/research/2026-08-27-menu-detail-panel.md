# Research — Menü + Részletező panel UX: Svájci térkép appok mintái

- **Dátum:** 2026-08-27
- **Szerző:** researcher (standing goal: „legyen felhasználóbarát de meg lehessen találni minden információt")
- **Státusz:** draft → ADR-010 input
- **Kapcsolódik:** `frontend/src/app/[locale]/page.tsx` (269 sor monolitikus), ADR-001 (Next.js + MapLibre/Three.js stack), `messages/{de,en,fr,it}.json`

---

## 1. Probléma

A Swiss P Map jelenleg egy **3D rendering engine bemutató**: a térkép teljes viewport, alatta egyetlen lapos kártya 4 tabbal. Nincs:
- **Navigációs menü** (témák kiválasztása)
- **Részletező panel** (kiválasztott egység adatai)
- **Hierarchia** (kontextus → választás → részletek)

A felhasználó nem tudja: „mit nézek?", „mi a következő?", „hol vannak a részletek?".

## 2. Versenytárs/OGD minták (élő curl 2026-08-27)

### geo.admin.ch (swisstopo)
- **Layout:** Bal sidebar (rétegek, szűrők) + térkép jobbra + alul/Gomb panel (FeatureInfo)
- **Minta:** réteg választás → térkép reagál → kattintás → FeatureInfo panel alul
- **Tanulság:** sidebar = navigáció, panel = kontextuális részletek

### map.zh.ch (ZH GIS)
- **Layout:** Bal sidebar (összes réteg csoportosítva: Politik, Környezet, Építés) + térkép + alul Térképinformáció panel
- **Minta:** kategória → réteg → kattint → érték megjelenítés

### Houzy Pro (ingatlan)
- **Layout:** Bal oszlop (lista + szűrők) + jobb térkép/lakás részletek
- **Minta:** lista elem kiválasztás → részletes nézet

### smartconext (B2B)
- **Layout:** Bal menü (Dashboard, Eszközök, Riasztások) + fő tartalom panel
- **Minta:** főmenü → altéma → részletes tartalom

## 3. Összehasonlítás — UX opciók

| Szempont | **A: Bal sidebar + Alul panel** | **B: Felső menü sor + Középső panel** | **C: Alsó sáv + Felfelé csúszó részletező** |
|---|---|---|---|
| **Érték** (felhasználóbarátság) | **5** — svájci OGD standard, intuitív | 4 — mobilbarát, de kevesebb hely | 3 — rejtett, nem nyilvánvaló |
| **Térkép hely** (5=legtöbb) | 4 — sidebar 25% elfoglal | **5** — minimális overhead | **5** — teljes viewport |
| **Mélység** (részletezhetőség) | **5** — sidebar + panel = 2 szint | 3 — csak 1 panel | 4 — panel nőhet |
| **Karbantarthatóság** | **4** — React komponensek szétválasztva | 4 — egyszerű | 3 — animáció kezelés |
| **Responsive** | 4 — sidebar mobilra összecsuk | **5** — természetesen flex | 4 — bottom sheet minta |
| **Súlyozott össz** | **4.5 🏆** | **4.0** | **3.6** |

**Nyertes: Opció A — Bal sidebar + Alul részletező panel** (másolja a geo.admin.ch mintáját, amit a svájci felhasználók már ismernek).

## 4. Javasolt layout

```
┌───────────────────────────────────────────────────────┐
│ [Header: Swiss P Map + nyelvváltó]                     │
├────────┬──────────────────────────────────────────────┤
│        │                                               │
│ MENU   │              MAP (3D / 2D)                    │
│ ─────  │              (teljes viewport)                 │
│ 🏛 Politik│                                            │
│ 📍 Ort  │              [kattintás → részletező]        │
│ 🏗 Planung│                                            │
│ ☀ Sonnendach│                                         │
│ ⚖ ÖREB │                                            │
│ 📊 Összes│                                            │
│        │                                               │
├────────┴──────────────────────────────────────────────┤
│ DETAIL PANEL (kiválasztott egység részletei)           │
│ [Fejléc: PLZ / település neve]                         │
│ [Tartalom: kiválasztott témához tartozó adatok]         │
└───────────────────────────────────────────────────────┘
```

**Működés:**
1. Sidebar-ban kiválasztod a témát (Pl. „Politik")
2. A térkép reagál (kijelöli a releváns réteget)
3. A bal panel listázza a releváns egységeket (Pl. Wahlkreis 4+5, Nationalrat)
4. Kattintás egy elemre → alul megjelenik a részletező panel (képviselő neve, pártja, indítványai)

## 5. Implementációs komponensek

| Komponens | Felelősség | Méret becslés |
|---|---|---|
| `TopicSidebar.tsx` | Bal menü: téma ikon + cím + számjelzés, `activeTopic` state | ~80 sor |
| `TopicList.tsx` | Sidebar-beli lista: kiválasztott témához tartozó elemek | ~120 sor |
| `DetailPanel.tsx` | Alul részletező: kiválasztott elem adatai (dinamikus sablon) | ~100 sor |
| `page.tsx` (refaktor) | Layout keret: sidebar + map + detail, `activeTopic` + `selectedItem` state | ~200 sor (max 400) |
| `Map3D.tsx` (bővítés) | `highlightTopic(topic)` prop — térkép reagál a témaválasztásra | +30 sor |
| `messages/*.json` | Új kulcsok: `menu.*`, `detail.*`, `list.*` | +40 sor/nyelv |

## 6. Témakörök (sidebar)

| Téma | Ikon | Adatforrás | Sidebar lista tartalma | DetailPanel tartalma |
|---|---|---|---|---|
| **Összes** | 📊 | PlaceInfo összes | Összefoglaló kártya (6 csempe) | KI-Zusammenfassung 2 mondat |
| **Politik** | 🏛 | politics?live=true | Wahlkreis + Nationalratok | Képviselő neve, pártja, indítványai |
| **Ort** | 📍 | place?live=true | 6 csempe (Steuer, Lärm, ÖV, GWR, Solar, ÖREB) | Kiválasztott csempe részlete |
| **Planung** | 🏗 | planning/baugesuche | Baugesuche lista (cím + nap) | Baugesuch részletes (cím, határidő, térkép) |
| **Sonnendach** | ☀ | place solar | Solar osztály + kWh/m² | BFE adatok, potenciál |
| **ÖREB** | ⚖ | place oereb | Nutzungszone | ÖREB leírás, zónatípus |

## 7. UX folyamat (felhasználói út)

1. **Kezdőképernyő:** 3D térkép + sidebar „Összes" kiválasztva → alul KI-összefoglaló + 6 csempe
2. **PLZ keresés:** Sidebar-ban „8004" begépelve → térkép zoom Zürich → lista frissül → alul részletező
3. **Téma váltás:** Kattintás „Politik" → lista: Wahlkreis 4+5, Nationalrat→Röthlisberger/Steuri → kattintás → alul: képviselő profil
4. **Vissza:** „Összes" kattintás → vissza az összefoglalóhoz

## 8. Források

1. `geo.admin.ch` — bal sidebar + FeatureInfo panel minta (2026-08-27 live)
2. `map.zh.ch` — kategória→réteg→panel hierarchia (2026-08-27 live)
3. ADR-001 (accepted): Next.js + Three.js stack — komponens szétválasztás meglévő
4. `page.tsx` 269 sor — refaktorálás nem növeli, csak szétválasztja
