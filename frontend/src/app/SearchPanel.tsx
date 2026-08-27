"use client";

import { useState } from "react";
import { useTranslations } from "next-intl";
import { api, type Baugesuch, type DistrictRepresentatives, type PlaceInfo } from "@/lib/api";
import { resolveQuery } from "./postcode_coords";

interface Result {
  place?: PlaceInfo;
  politics?: DistrictRepresentatives;
  baugesuche?: Baugesuch[];
  error?: string;
  lngLat?: [number, number] | null;
}

const QUICK_PICKS = [
  { label: "8004 Aussersihl", code: "8004" },
  { label: "8001 Altstadt", code: "8001" },
  { label: "8610 Uster", code: "8610" },
  { label: "3011 Bern", code: "3011" },
  { label: "4001 Basel", code: "4001" },
];

export default function SearchPanel({ onResult }: { onResult: (r: Result) => void }) {
  const t = useTranslations();
  const [query, setQuery] = useState("8004");
  const [loading, setLoading] = useState(false);

  function isPostcode(q: string): boolean {
    return /^\d{4}$/.test(q.trim());
  }

  async function executeSearch(targetQuery: string) {
    const q = targetQuery.trim();
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
          onResult({ error: t("search.errorNotFound", { query: q }) });
        }
      }
    } catch {
      onResult({ error: t("search.errorNoData", { query: q }) });
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="flex flex-col gap-2">
      <div className="flex flex-wrap items-center gap-2">
        <input
          className="w-full sm:w-80 rounded-lg border border-white/15 bg-white/[0.07] px-3.5 py-2 text-sm text-slate-100 placeholder:text-slate-500 focus:border-sky-400 focus:outline-none focus:ring-1 focus:ring-sky-400"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          placeholder={t("search.placeholder")}
          onKeyDown={(e) => e.key === "Enter" && executeSearch(query)}
          data-testid="search-input"
        />
        <button
          className="rounded-lg bg-sky-600 px-4 py-2 text-sm font-medium text-white shadow-sm transition hover:bg-sky-500 disabled:opacity-50"
          onClick={() => executeSearch(query)}
          disabled={loading || query.trim().length < 2}
          data-testid="search-button"
        >
          {loading ? "…" : t("search.button")}
        </button>
      </div>

      {/* Quick-pick shortcuts */}
      <div className="flex flex-wrap items-center gap-1.5 text-xs text-slate-400">
        <span className="text-slate-500 text-[11px] font-medium uppercase tracking-wider">Quick:</span>
        {QUICK_PICKS.map((qp) => (
          <button
            key={qp.code}
            onClick={() => {
              setQuery(qp.code);
              executeSearch(qp.code);
            }}
            className="rounded-md border border-white/10 bg-white/[0.04] px-2 py-0.5 text-slate-300 transition hover:border-sky-400/50 hover:bg-sky-500/15 hover:text-sky-200"
          >
            {qp.label}
          </button>
        ))}
      </div>
    </div>
  );
}
