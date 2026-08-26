"use client";

import { useState } from "react";
import dynamic from "next/dynamic";
import SearchPanel from "./SearchPanel";
import type { Baugesuch, DistrictRepresentatives, PlaceInfo } from "@/lib/api";

// ADR-003: a régi fehér MapLibre helyett a 3D sematikus térkép jelenik meg
const Map3D = dynamic(() => import("./Map3D"), { ssr: false });

interface Result {
  place?: PlaceInfo;
  politics?: DistrictRepresentatives;
  baugesuche?: Baugesuch[];
  error?: string;
  lngLat?: [number, number] | null;
}

export default function Home() {
  const [result, setResult] = useState<Result | null>(null);

  return (
    <main className="min-h-screen bg-[#030712] text-gray-100">
      {/* 3D Térkép — full bleed, maximális hatás */}
      <Map3D selectedPostcode={result?.place?.postcode ?? null} baugesuche={result?.baugesuche ?? []} />

      {/* Alsó sáv: kereső + adatpanel */}
      <div className="mx-auto max-w-5xl px-6 py-5">
        <SearchPanel onResult={setResult} />

        {result?.error && <p className="mt-3 text-sm text-amber-400">{result.error}</p>}

        {result?.place && (
          <ul className="mt-3 grid grid-cols-2 gap-x-6 gap-y-2 rounded-lg border border-white/10 bg-white/[0.03] p-4 text-sm backdrop-blur-sm">
            <li>
              <span className="text-slate-500">Steuerfuss: </span>
              <span className="font-semibold text-slate-100">{result.place.steuerfuss_percent}%</span>
            </li>
            <li>
              <span className="text-slate-500">Zaj (nappal): </span>
              <span className="font-semibold text-slate-100">{result.place.noise_db_day} dB(A)</span>
            </li>
            <li>
              <span className="text-slate-500">ÖV: </span>
              <span className="font-semibold text-slate-100">Klasse {result.place.oev_class}</span>
            </li>
            <li>
              <span className="text-slate-500">Gemeinde: </span>
              <span className="font-semibold text-slate-100">
                {result.place.municipality} ({result.place.canton})
              </span>
            </li>
            {result.politics && (
              <>
                <li>
                  <span className="text-slate-500">Wahlkreis: </span>
                  <span className="font-semibold text-slate-100">{result.politics.district_name}</span>
                </li>
                <li>
                  <span className="text-slate-500">Képviselők: </span>
                  <span className="font-semibold text-slate-100">
                    {result.politics.representatives.map((r) => `${r.name} (${r.party})`).join(", ")}
                  </span>
                </li>
              </>
            )}
            {result.baugesuche !== undefined && (
              <li className="col-span-2 pt-2 border-t border-white/10">
                <span className="text-slate-500">Baugesuche (Auflage aktiv): </span>
                {result.baugesuche.length === 0 ? (
                  <span className="text-slate-400">keine aktiven im 20-Tage Fenster</span>
                ) : (
                  <span className="font-semibold text-amber-300">
                    {result.baugesuche.length} aktiv — Einsprache möglich
                  </span>
                )}
                {result.baugesuche.length > 0 && (
                  <ul className="mt-1 space-y-1 text-xs">
                    {result.baugesuche.slice(0, 5).map((b) => (
                      <li key={b.id} className="truncate">
                        <a href={b.source_url} target="_blank" rel="noreferrer" className="text-sky-400 hover:underline">
                          {b.title}
                        </a>{" "}
                        <span className="text-slate-500">— {b.municipality} · Aufl. bis {b.auflage_end}</span>
                      </li>
                    ))}
                  </ul>
                )}
              </li>
            )}
          </ul>
        )}

        <p className="mt-4 text-xs text-slate-600">
          Adatok: <code className="text-slate-500">/api/v1/place</code> ·{" "}
          <code className="text-slate-500">/api/v1/politics</code> ·{" "}
          <code className="text-slate-500">/api/v1/planning</code> · Three.js + Swisstopo boundaries
        </p>
      </div>
    </main>
  );
}
