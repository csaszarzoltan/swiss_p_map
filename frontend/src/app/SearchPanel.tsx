"use client";

import { useState } from "react";
import { api, type Baugesuch, type DistrictRepresentatives, type PlaceInfo } from "@/lib/api";
import { resolveQuery } from "./postcode_coords";

interface Result {
  place?: PlaceInfo;
  politics?: DistrictRepresentatives;
  baugesuche?: Baugesuch[];
  error?: string;
  lngLat?: [number, number] | null;
}

export default function SearchPanel({ onResult }: { onResult: (r: Result) => void }) {
  const [query, setQuery] = useState("8004");
  const [loading, setLoading] = useState(false);

  function isPostcode(q: string): boolean {
    return /^\d{4}$/.test(q.trim());
  }

  async function search() {
    const q = query.trim();
    if (q.length < 2) return;
    setLoading(true);
    try {
      if (isPostcode(q)) {
        const [place, politics, planning] = await Promise.all([
          api.place(q),
          api.politics(q),
          api.planning(q, true).catch(() => ({ items: [] as Baugesuch[] })),
        ]);
        const lngLat = await import("./postcode_coords").then((m) => m.resolvePostcode(q));
        onResult({ place, politics, baugesuche: planning.items, lngLat, error: undefined });
      } else {
        const lngLat = await resolveQuery(q);
        if (lngLat) {
          onResult({ lngLat, error: undefined });
        } else {
          onResult({ error: `Nincs találat: „${q}"` });
        }
      }
    } catch {
      onResult({ error: `Nincs adat: ${query.trim()}` });
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
        data-testid="search-input"
      />
      <button
        className="bg-sky-600 text-white rounded px-4 py-2 text-sm disabled:opacity-50"
        onClick={search}
        disabled={loading || query.trim().length < 2}
        data-testid="search-button"
      >
        {loading ? "…" : "Keresés"}
      </button>
    </div>
  );
}
