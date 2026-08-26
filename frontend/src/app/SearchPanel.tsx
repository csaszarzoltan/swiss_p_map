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
        onResult({ place, politics, error: undefined });
      } else {
        onResult({ error: `Keresés: „${q}" — térkép pozicionálva (részletes adatok PLZ-re érhetők el)` });
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
