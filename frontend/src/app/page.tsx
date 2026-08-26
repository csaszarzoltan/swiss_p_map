"use client";

import { useState } from "react";
import dynamic from "next/dynamic";
import SearchPanel from "./SearchPanel";
import type { DistrictRepresentatives, PlaceInfo } from "@/lib/api";

const Map = dynamic(() => import("./Map"), { ssr: false });

interface Result {
  place?: PlaceInfo;
  politics?: DistrictRepresentatives;
  error?: string;
}

export default function Home() {
  const [result, setResult] = useState<Result | null>(null);

  return (
    <main className="mx-auto max-w-5xl p-6">
      <h1 className="text-2xl font-bold">Swiss P Map</h1>
      <p className="text-sm text-zinc-600">
        „A svájci környék egyetlen térképén” — Zürich pilot (ADR-001)
      </p>

      <Map />

      <SearchPanel onResult={setResult} />

      {result?.error && <p className="mt-3 text-sm text-amber-700">{result.error}</p>}

      {result?.place && (
        <ul className="mt-3 text-sm space-y-1 rounded border p-3 bg-zinc-50">
          <li>
            <strong>Steuerfuss:</strong> {result.place.steuerfuss_percent}%
          </li>
          <li>
            <strong>Zaj (nappal):</strong> {result.place.noise_db_day} dB(A)
          </li>
          <li>
            <strong>ÖV:</strong> Klasse {result.place.oev_class}
          </li>
          <li>
            <strong>Gemeinde:</strong> {result.place.municipality} ({result.place.canton})
          </li>
          {result.politics && (
            <>
              <li>
                <strong>Wahlkreis:</strong> {result.politics.district_name}
              </li>
              <li>
                <strong>Képviselők:</strong>{" "}
                {result.politics.representatives.map((r) => `${r.name} (${r.party})`).join(", ")}
              </li>
            </>
          )}
        </ul>
      )}

      <p className="mt-3 text-xs text-zinc-500">
        Backend: <code>/api/v1/place/8004</code> · Swisstopo Light basemap
      </p>
    </main>
  );
}
