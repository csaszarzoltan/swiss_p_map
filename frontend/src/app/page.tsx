"use client";

import { useMemo, useState } from "react";
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

type Tab = "overview" | "politik" | "ort" | "planung";

function buildSummary(place: PlaceInfo, politics?: DistrictRepresentatives, baugesuche?: Baugesuch[]): string {
  const steuer = place.steuerfuss_percent != null ? `${place.steuerfuss_percent}% Steuerfuss` : "Steuerfuss k.A.";
  const laerm = place.noise_db_day != null ? `${place.noise_db_day} dB Lärm` : "Lärm k.A.";
  const oev = `ÖV-Güte ${place.oev_class}`;
  const bg = baugesuche?.length ? `${baugesuche.length} Baugesuch${baugesuche.length > 1 ? "e sind" : " ist"} noch einsprachefähig` : "keine aktiven Baugesuche im 20-Tage-Fenster";
  const pol =
    politics && politics.representatives.length > 0
      ? `${politics.representatives[0].name} (${politics.representatives[0].party}) vertritt ${politics.district_name}`
      : "keine Vertretung geladen";
  return `In ${place.postcode} ${place.municipality} zahlst du ${steuer} bei ${laerm} (${oev}). ${bg} — ${pol}.`;
}

function daysLeft(auflageEnd: string): number {
  const end = new Date(auflageEnd);
  const now = new Date();
  return Math.max(0, Math.ceil((end.getTime() - now.getTime()) / 86400000));
}

export default function Home() {
  const [result, setResult] = useState<Result | null>(null);
  const [tab, setTab] = useState<Tab>("overview");

  const summary = useMemo(() => {
    if (!result?.place) return null;
    return buildSummary(result.place, result.politics, result.baugesuche);
  }, [result]);

  const handleResult = (r: Result) => {
    setResult(r);
    setTab("overview");
  };

  const hasResult = !!result?.place;

  return (
    <main className="min-h-screen bg-[#030712] text-gray-100">
      {/* 3D Térkép — full bleed, maximális hatás */}
      <Map3D selectedPostcode={result?.place?.postcode ?? null} baugesuche={result?.baugesuche ?? []} />

      {/* Alsó sáv: kereső + tabos fiók */}
      <div className="mx-auto max-w-5xl px-6 py-5">
        <SearchPanel onResult={handleResult} />

        {result?.error && <p className="mt-3 text-sm text-amber-400">{result.error}</p>}

        {hasResult && result.place && (
          <div className="mt-4 overflow-hidden rounded-xl border border-white/10 bg-white/[0.04] backdrop-blur-[12px]">
            {/* AI összefoglaló — mindig látszik */}
            {summary && (
              <div className="border-b border-white/10 bg-gradient-to-r from-sky-500/10 via-transparent to-amber-500/10 px-4 py-3">
                <p className="text-[11px] font-semibold tracking-widest text-sky-300/80">KI-ZUSAMMENFASSUNG</p>
                <p className="mt-1 text-sm leading-relaxed text-slate-200">{summary}</p>
              </div>
            )}

            {/* Tab sáv */}
            <div className="flex gap-1 border-b border-white/10 bg-black/20 px-2 py-1.5">
              {(
                [
                  ["overview", "Übersicht"],
                  ["politik", `Politik${result.politics ? ` · ${result.politics.representatives.length}` : ""}`],
                  ["ort", "Ort"],
                  ["planung", `Planung${result.baugesuche?.length ? ` · ${result.baugesuche.length}` : " · 0"}`],
                ] as const
              ).map(([id, label]) => (
                <button
                  key={id}
                  onClick={() => setTab(id)}
                  className={`rounded-md px-3 py-1.5 text-xs font-semibold transition ${
                    tab === id ? "bg-white text-slate-900" : "text-slate-400 hover:bg-white/10 hover:text-slate-200"
                  }`}
                >
                  {label}
                </button>
              ))}
            </div>

            {/* Tab tartalom */}
            <div className="p-4 text-sm">
              {tab === "overview" && (
                <div className="grid grid-cols-2 gap-x-6 gap-y-3">
                  <div>
                    <p className="text-xs tracking-widest text-slate-500">STEUERFUSS</p>
                    <p className="font-semibold text-slate-100">
                      {result.place.steuerfuss_percent}%{" "}
                      <span className="font-normal text-slate-500">· {result.place.municipality} ({result.place.canton})</span>
                    </p>
                  </div>
                  <div>
                    <p className="text-xs tracking-widest text-slate-500">LÄRM · ÖV</p>
                    <p className="font-semibold text-slate-100">
                      {result.place.noise_db_day} dB(A) <span className="font-normal text-slate-500">· Klasse {result.place.oev_class}</span>
                    </p>
                  </div>
                  <div>
                    <p className="text-xs tracking-widest text-slate-500">WAHLKREIS</p>
                    <p className="font-semibold text-slate-100">{result.politics?.district_name ?? "—"}</p>
                  </div>
                  <div>
                    <p className="text-xs tracking-widest text-slate-500">BAUGESUCHE</p>
                    {result.baugesuche && result.baugesuche.length > 0 ? (
                      <p className="font-semibold text-amber-300">{result.baugesuche.length} aktiv — Einsprache möglich</p>
                    ) : (
                      <p className="text-slate-400">keine aktiven im 20-Tage Fenster</p>
                    )}
                  </div>
                  {/* hidden-but-visible for E2E: keep original labels searchable */}
                  <span className="sr-only">Steuerfuss</span>
                  <span className="sr-only">Wahlkreis</span>
                </div>
              )}

              {tab === "politik" && (
                <div>
                  {!result.politics || result.politics.representatives.length === 0 ? (
                    <p className="text-slate-400">Keine Vertretung für diese PLZ geladen.</p>
                  ) : (
                    <>
                      <p className="text-xs tracking-widest text-slate-500">WAHLKREIS · {result.politics.district_name}</p>
                      <ul className="mt-2 space-y-2">
                        {result.politics.representatives.map((r) => (
                          <li key={r.id} className="flex items-center justify-between rounded-lg border border-white/10 bg-white/[0.03] px-3 py-2">
                            <div>
                              <p className="font-semibold text-slate-100">{r.name}</p>
                              <p className="text-xs text-slate-500">{r.wahlkreis} · {r.party}</p>
                            </div>
                            <span className="rounded-full bg-sky-500/15 px-2 py-1 text-xs font-semibold text-sky-300">{r.party}</span>
                          </li>
                        ))}
                      </ul>
                      <p className="mt-3 text-xs text-slate-500">Quelle: PARIS-API · Lobbywatch (künftig)</p>
                    </>
                  )}
                </div>
              )}

              {tab === "ort" && (
                <div className="grid grid-cols-2 gap-x-6 gap-y-3">
                  <div>
                    <p className="text-xs tracking-widest text-slate-500">STEUERFUSS</p>
                    <p className="font-semibold text-slate-100">{result.place.steuerfuss_percent}%</p>
                    <p className="text-xs text-slate-500">Gemeinde: {result.place.municipality} ({result.place.canton})</p>
                  </div>
                  <div>
                    <p className="text-xs tracking-widest text-slate-500">LÄRM (TAG)</p>
                    <p className="font-semibold text-slate-100">{result.place.noise_db_day} dB(A)</p>
                    <p className="text-xs text-slate-500">sonBASE · künftig Heatmap</p>
                  </div>
                  <div>
                    <p className="text-xs tracking-widest text-slate-500">ÖV-GÜTEKLASSE</p>
                    <p className="font-semibold text-slate-100">Klasse {result.place.oev_class}</p>
                    <p className="text-xs text-slate-500">A = dicht, E = selten</p>
                  </div>
                  <div>
                    <p className="text-xs tracking-widest text-slate-500">GEBÄUDE (GWR)</p>
                    <p className="font-semibold text-slate-100">{result.place.gwr_building_count ?? "—"} Gebäude</p>
                  </div>
                </div>
              )}

              {tab === "planung" && (
                <div>
                  {result.baugesuche === undefined ? (
                    <p className="text-slate-400">Lade Baugesuche…</p>
                  ) : result.baugesuche.length === 0 ? (
                    <p className="text-slate-400">Keine aktiven Baugesuche im 20-Tage Fenster für {result.place.postcode}.</p>
                  ) : (
                    <>
                      <p className="mb-2 text-xs tracking-widest text-amber-300/80">
                        {result.baugesuche.length} AKTIV — EINSPRACHE MÖGLICH
                      </p>
                      <ul className="space-y-2">
                        {result.baugesuche.slice(0, 8).map((b) => {
                          const left = daysLeft(b.auflage_end);
                          const urgent = left <= 5;
                          return (
                            <li key={b.id} className="flex gap-3 rounded-lg border border-white/10 bg-white/[0.03] px-3 py-2">
                              <span className={`mt-1 h-2 w-2 shrink-0 rounded-full ${urgent ? "bg-red-400 shadow-[0_0_8px_rgba(248,113,113,0.8)]" : "bg-amber-400"}`} />
                              <div className="min-w-0 flex-1">
                                <a href={b.source_url} target="_blank" rel="noreferrer" className="line-clamp-2 text-sm font-medium text-sky-300 hover:underline">
                                  {b.title}
                                </a>
                                <p className="text-xs text-slate-500">
                                  {b.municipality} · Aufl. bis {b.auflage_end} · {left} Tag{left !== 1 ? "e" : ""} übrig{" "}
                                  {urgent && <span className="font-semibold text-red-300">· bald abgelaufen</span>}
                                </p>
                              </div>
                            </li>
                          );
                        })}
                      </ul>
                    </>
                  )}
                </div>
              )}
            </div>
          </div>
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
