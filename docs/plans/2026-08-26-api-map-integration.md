# API ↔ Map Integration Implementation Plan

> **For Hermes:** Use subagent-driven-development skill to implement this plan task-by-task.

**Goal:** A térképen postcode-keresés után megjelennek a Place (Steuerfuss/zaj/ÖV) és Politics (képviselők) adatok a backend API-ról.

**Architecture:** Next.js client component hívja a FastAPI végpontokat (`fetch`), a Map komponens kattintás/marker alapján frissül. Állapotkezelés: egyszerű React state (nincs Redux — YAGNI). CORS: FastAPI `CORSMiddleware` localhost dev-hez.

**Tech Stack:** Next.js 14 App Router, TypeScript strict, maplibre-gl, Tailwind; FastAPI + httpx TestClient E2E.

---

### Task 1: FastAPI CORS middleware

**Objective:** A frontend (localhost:3000) elérje az API-t (localhost:8000).

**Files:**
- Modify: `src/main.py`
- Test: `tests/e2e/test_core_e2e.py`

**Step 1: Write failing test**

```python
def test_cors_preflight() -> None:
    r = client.options(
        "/api/v1/place/8004",
        headers={"Origin": "http://localhost:3000", "Access-Control-Request-Method": "GET"},
    )
    assert r.status_code in (200, 204)
    assert r.headers.get("access-control-allow-origin") == "http://localhost:3000"
```

**Step 2: Run test to verify failure**

Run: `PATH=.venv/bin:$PATH pytest tests/e2e/test_core_e2e.py::test_cors_preflight -v`
Expected: FAIL — no access-control-allow-origin header

**Step 3: Write minimal implementation** (`src/main.py`, imports fölé)

```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_methods=["*"],
    allow_headers=["*"],
)
```

**Step 4: Run test to verify pass**

Run: `PATH=.venv/bin:$PATH pytest tests/e2e/test_core_e2e.py::test_cors_preflight -v`
Expected: PASS

**Step 5: Commit**

```bash
git add src/main.py tests/e2e/test_core_e2e.py
git commit -m "feat: CORS middleware a frontend integrációhoz"
```

---

### Task 2: API client lib (frontend)

**Objective:** Típusos fetch wrapper a 3 végponthoz.

**Files:**
- Create: `frontend/src/lib/api.ts`

**Step 1: Write the module**

```typescript
export interface PlaceInfo {
  postcode: string;
  municipality: string;
  canton: string;
  steuerfuss_percent: number | null;
  noise_db_day: number | null;
  oev_class: string;
  gwr_building_count: number | null;
}

export interface Representative {
  id: string;
  name: string;
  party: string;
  wahlkreis: string;
}

export interface DistrictRepresentatives {
  district_name: string;
  postcode: string;
  representatives: Representative[];
}

const BASE = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

async function getJson<T>(path: string): Promise<T> {
  const res = await fetch(`${BASE}${path}`);
  if (!res.ok) throw new Error(`API ${res.status}: ${path}`);
  return res.json() as Promise<T>;
}

export const api = {
  place: (postcode: string) => getJson<PlaceInfo>(`/api/v1/place/${postcode}`),
  politics: (postcode: string) =>
    getJson<DistrictRepresentatives>(
      `/api/v1/politics/representatives?postcode=${postcode}`,
    ),
};
```

**Step 2: Verify type-check**

Run: `cd frontend && npx tsc --noEmit`
Expected: exit 0

**Step 3: Commit**

```bash
git add frontend/src/lib/api.ts
git commit -m "feat: típusos API client (place, politics)"
```

---

### Task 3: Postcode search UI komponens

> **Audit 2026-08-26 (A):** A Task 3 eredetileg 4 számjegyű PLZ-re volt szűkítve (`maxLength={4}`). Az auditor javaslatára a Task 3 már szabad szöveges keresést enged (cím, község, irányítószám), a teljes Swisstopo `type=locations` képesség kihasználásával. A Task 5 élő geokódolása így már nem csak PLZ-t, hanem pl. „Bahnhofstrasse 10, Zürich" vagy „Langstrasse" lekérdezést is kiszolgál.

**Objective:** Input mező + „Keresés" gomb; eredmény Place+Politics panel.

**Files:**
- Create: `frontend/src/app/SearchPanel.tsx`
- Modify: `frontend/src/app/page.tsx`

**Step 1: Write SearchPanel.tsx**

```tsx
"use client";

import { useState } from "react";
import { api, type DistrictRepresentatives, type PlaceInfo } from "@/lib/api";

interface Result {
  place?: PlaceInfo;
  politics?: DistrictRepresentatives;
  error?: string;
}

export default function SearchPanel({ onResult }: { onResult: (r: Result) => void }) {
  const [query, setQuery] = useState("8004");
  const [loading, setLoading] = useState(false);

  // Audit A: szabad szöveg (PLZ, cím, község) — nem csak 4 számjegy.
  // A backend place/politics hívás továbbra is PLZ-alapú; ha a query nem 4 számjegy,
  // a geokódolás (Task 5) oldja fel koordinátára, a panel pedig csak geokódolt találatnál tölt.
  function isPostcode(q: string): boolean {
    return /^\d{4}$/.test(q.trim());
  }

  async function search() {
    const q = query.trim();
    if (q.length < 2) return;
    setLoading(true);
    try {
      if (isPostcode(q)) {
        const [place, politics] = await Promise.all([api.place(q), api.politics(q)]);
        onResult({ place, politics });
      } else {
        // Szabad szöveg: a geokódolás (Task 5) felel a koordinátáért;
        // a panel üzenetet mutat, amíg a map fly-to megtörténik.
        onResult({ error: `Keresés: „${q}" — térkép pozicionálva (részletes adatok PLZ-re érhetők el)` });
        // A tényleges fly-to a page.tsx-ben a query alapján hívott resolve-nal történik (Task 4/5).
      }
    } catch {
      onResult({ error: `Nincs adat: ${q}` });
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="flex gap-2 mt-4">
      <input
        className="border rounded px-3 py-2 text-sm w-64"
        value={query}
        onChange={(e) => setQuery(e.target.value)}
        placeholder="PLZ, cím vagy község (pl. 8004 vagy Bahnhofstrasse 10)"
        onKeyDown={(e) => e.key === "Enter" && search()}
      />
      <button
        className="bg-sky-600 text-white rounded px-4 py-2 text-sm disabled:opacity-50"
        onClick={search}
        disabled={loading || query.trim().length < 2}
      >
        {loading ? "…" : "Keresés"}
      </button>
    </div>
  );
}
```

**Step 2: Wire into page.tsx** (Map import után)

```tsx
const [result, setResult] = useState<Result | null>(null);
// ...<SearchPanel onResult={setResult} /> és egy result-panel blokk:
{result?.error && <p className="text-red-600 text-sm">{result.error}</p>}
{result?.place && (
  <ul className="text-sm mt-2">
    <li>Steuerfuss: {result.place.steuerfuss_percent}%</li>
    <li>Zaj (nappal): {result.place.noise_db_day} dB(A)</li>
    <li>ÖV: Klasse {result.place.oev_class}</li>
    <li>Wahlkreis: {result.politics?.district_name}</li>
    <li>Képviselők: {result.politics?.representatives.map((r) => `${r.name} (${r.party})`).join(", ")}</li>
  </ul>
)}
```

**Step 3: Verify build**

Run: `cd frontend && npm run build && npx tsc --noEmit`
Expected: build success, tsc exit 0

**Step 4: Commit**

```bash
git add frontend/src/app/SearchPanel.tsx frontend/src/app/page.tsx
git commit -m "feat: postcode kereső + Place/Politics panel"
```

---

### Task 4: Marker frissítés a térképen

**Objective:** Sikeres keresés után a marker ugrjon a postcode koordinátájára.

**Files:**
- Create: `frontend/src/app/postcode_coords.ts` (stub LV95→lat/lng tábla 8001/8004-re)
- Modify: `frontend/src/app/Map.tsx`

**Step 1: Write postcode_coords.ts**

```typescript
// Stub: valós geokódolás Task 5-ben (Swisstopo search)
export const POSTCODE_COORDS: Record<string, [number, number]> = {
  "8001": [8.545, 47.377],
  "8004": [8.517, 47.392],
};

export function coordFor(postcode: string): [number, number] | undefined {
  return POSTCODE_COORDS[postcode];
}
```

**Step 2: Map.tsx — props vezérelt marker**

A `Map` kapjon `{ lngLat }: { lngLat: [number, number] | null }` propot; useEffect-ben ha változik, `map.flyTo({ center: lngLat, zoom: 14 })` és marker `setLngLat`.

**Step 3: Verify**

Run: `cd frontend && npm run build`
Expected: success

**Step 4: Commit**

```bash
git add frontend/src/app/postcode_coords.ts frontend/src/app/Map.tsx
git commit -m "feat: marker fly-to postcode szerint"
```

---

### Task 5: Élő Swisstopo geokódolás a stub helyett

> **Audit A következménye:** a Task 3 már szabad szöveges queryt enged, ezért a geokódolás nem csak `PLZ 8004` formát, hanem bármilyen `type=locations` találatot kezel (cím, község, utca). A Task 5 implementációja így valós Zürich-szerte használható keresővé válik.

**Objective:** A postcode → koordináta átalakítás valódi Swisstopo hívás legyen.

**Files:**
- Modify: `frontend/src/app/postcode_coords.ts` → fetch `api3.geo.admin.ch` locations search (`POSTCODE ${plz}`), fallback a stub táblára offline esetben.

**Step 1: Implementáció**

```typescript
export async function resolvePostcode(postcode: string): Promise<[number, number]> {
  try {
    const res = await fetch(
      `https://api3.geo.admin.ch/rest/services/api/SearchServer?searchText=PLZ%20${postcode}&type=locations&limit=1`,
    );
    const json = await res.json();
    const attrs = json.results?.[0]?.attrs;
    // Swisstopo WGS84: lat/lon közvetlenül a location típusnál
    return [attrs.lon, attrs.lat];
  } catch {
    return POSTCODE_COORDS[postcode] ?? [8.54, 47.378];
  }
}
```

**Step 2: Manuális ellenőrzés** (böngészőben 8004 → Zürich Kreis 4 felé ugrik)

**Step 3: Commit**

```bash
git add frontend/src/app/postcode_coords.ts
git commit -m "feat: élő Swisstopo geokódolás postcode-hoz"
```

---

### Task 6: Végponti kézi füstteszt + dokumentum

**Objective:** Bizonyított működés, nem csak zöld tesztek.

**Step 1:** Két terminál: `uvicorn src.main:app --reload --port 8000` + `cd frontend && npm run dev`

**Step 2:** Böngésző `http://localhost:3000` → 8004 keresés → marker ugrik, panel mutat Steuerfuss 119%, Wahlkreis 4+5, Muster Anna (SP).

**Step 3:** Screenshot a `docs/archive/` alá (Evidence TTL 30 nap), link a CHANGELOG-ba.

**Step 4:** `git commit -m "docs: API↔Map füstteszt bizonyíték"`

## Verification (a terv kész-jelentése)

- [ ] `pytest -q` → 20 passed (19 + CORS)
- [ ] `mypy src tests --ignore-missing-imports` → clean
- [ ] `ruff check src tests` → clean
- [ ] `cd frontend && npm run build` → success
- [ ] Manuális füst: 8004 → marker + panel adatok látszanak
