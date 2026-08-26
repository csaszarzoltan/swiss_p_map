"use client";

import { useMemo, useState } from "react";
import dynamic from "next/dynamic";
import {useTranslations} from 'next-intl';
import SearchPanel from "../SearchPanel";
import type { Baugesuch, DistrictRepresentatives, PlaceInfo } from "@/lib/api";

const Map3D = dynamic(() => import("../Map3D"), { ssr: false });

interface Result {
  place?: PlaceInfo;
  politics?: DistrictRepresentatives;
  baugesuche?: Baugesuch[];
  error?: string;
  lngLat?: [number, number] | null;
}

type Tab = "overview" | "politik" | "ort" | "planung";

function daysLeft(auflageEnd: string): number {
  const end = new Date(auflageEnd);
  const now = new Date();
  return Math.max(0, Math.ceil((end.getTime() - now.getTime()) / 86400000));
}

export default function Home() {
  const t = useTranslations();
  const [result, setResult] = useState<Result | null>(null);
  const [tab, setTab] = useState<Tab>("overview");

  const mapLocale = useMemo(() => ({
    title: t('map.title'),
    breadcrumb: t('map.breadcrumb'),
    subtitle: t('map.subtitle'),
    cantons: t('map.cantons'),
    population: t('map.population'),
    hint: t('map.hint'),
  }), [t]);

  const summary = useMemo(() => {
    if (!result?.place) return null;
    const p = result.place;
    const steuerLabel = p.steuerfuss_percent != null ? `${p.steuerfuss_percent}%` : t('summary.steuerFallback');
    const laerm = p.noise_db_day != null ? `${p.noise_db_day} dB` : t('summary.laermFallback');
    const oev = t('summary.oev', {klass: p.oev_class});
    const bg = result.baugesuche?.length
      ? (result.baugesuche.length === 1 ? t('summary.bgOne') : t('summary.bgMany', {count: result.baugesuche.length}))
      : t('summary.bgNone');
    const pol = result.politics && result.politics.representatives.length > 0
      ? t('summary.polWith', {name: result.politics.representatives[0].name, party: result.politics.representatives[0].party, district: result.politics.district_name})
      : t('summary.polNone');
    try {
      return t('summary.template', {postcode: p.postcode, municipality: p.municipality, steuer: steuerLabel, laerm, oev, bg, pol});
    } catch {
      return `${p.postcode} ${p.municipality} — ${steuerLabel} · ${laerm} · ${oev} — ${bg} — ${pol}`;
    }
  }, [result, t]);

  const handleResult = (r: Result) => {
    setResult(r);
    setTab("overview");
  };

  const hasResult = !!result?.place;

  return (
    <main className="min-h-screen bg-[#030712] text-gray-100">
      <Map3D selectedPostcode={result?.place?.postcode ?? null} baugesuche={result?.baugesuche ?? []} mapLocale={mapLocale} />

      <div className="mx-auto max-w-5xl px-6 py-5">
        <SearchPanel onResult={handleResult} />

        {result?.error && <p className="mt-3 text-sm text-amber-400">{result.error}</p>}

        {hasResult && result.place && (
          <div className="mt-4 overflow-hidden rounded-xl border border-white/10 bg-white/[0.04] backdrop-blur-[12px]">
            {summary && (
              <div className="border-b border-white/10 bg-gradient-to-r from-sky-500/10 via-transparent to-amber-500/10 px-4 py-3">
                <p className="text-[11px] font-semibold tracking-widest text-sky-300/80">{t('summary.label')}</p>
                <p className="mt-1 text-sm leading-relaxed text-slate-200">{summary}</p>
              </div>
            )}

            <div className="flex gap-1 border-b border-white/10 bg-black/20 px-2 py-1.5">
              {(
                [
                  ["overview", t('tabs.overview')],
                  ["politik", `${t('tabs.politik')}${result.politics ? ` · ${result.politics.representatives.length}` : ""}`],
                  ["ort", t('tabs.ort')],
                  ["planung", `${t('tabs.planung')}${result.baugesuche?.length ? ` · ${result.baugesuche.length}` : " · 0"}`],
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

            <div className="p-4 text-sm">
              {tab === "overview" && (
                <div className="grid grid-cols-2 gap-x-6 gap-y-3">
                  <div>
                    <p className="text-xs tracking-widest text-slate-500">{t('overview.steuerfuss')}</p>
                    <p className="font-semibold text-slate-100">
                      {result.place.steuerfuss_percent}%{" "}
                      <span className="font-normal text-slate-500">· {result.place.municipality} ({result.place.canton})</span>
                    </p>
                  </div>
                  <div>
                    <p className="text-xs tracking-widest text-slate-500">{t('overview.laermOev')}</p>
                    <p className="font-semibold text-slate-100">
                      {result.place.noise_db_day} dB(A) <span className="font-normal text-slate-500">· Klasse {result.place.oev_class}</span>
                    </p>
                  </div>
                  <div>
                    <p className="text-xs tracking-widest text-slate-500">{t('overview.wahlkreis')}</p>
                    <p className="font-semibold text-slate-100">{result.politics?.district_name ?? "—"}</p>
                  </div>
                  <div>
                    <p className="text-xs tracking-widest text-slate-500">{t('overview.baugesuche')}</p>
                    {result.baugesuche && result.baugesuche.length > 0 ? (
                      <p className="font-semibold text-amber-300">{t('overview.baugesucheActive', {count: result.baugesuche.length})}</p>
                    ) : (
                      <p className="text-slate-400">{t('overview.baugesucheNone')}</p>
                    )}
                  </div>
                  <span className="sr-only">Steuerfuss</span>
                  <span className="sr-only">Wahlkreis</span>
                </div>
              )}

              {tab === "politik" && (
                <div>
                  {!result.politics || result.politics.representatives.length === 0 ? (
                    <p className="text-slate-400">{t('politik.empty')}</p>
                  ) : (
                    <>
                      <p className="text-xs tracking-widest text-slate-500">{t('politik.wahlkreis', {name: result.politics.district_name})}</p>
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
                      <p className="mt-3 text-xs text-slate-500">{t('politik.source')}</p>
                    </>
                  )}
                </div>
              )}

              {tab === "ort" && (
                <div className="grid grid-cols-2 gap-x-6 gap-y-3">
                  <div>
                    <p className="text-xs tracking-widest text-slate-500">{t('ort.steuerfuss')}</p>
                    <p className="font-semibold text-slate-100">{result.place.steuerfuss_percent}%</p>
                    <p className="text-xs text-slate-500">{t('ort.gemeinde', {municipality: result.place.municipality, canton: result.place.canton})}</p>
                  </div>
                  <div>
                    <p className="text-xs tracking-widest text-slate-500">{t('ort.laermTag')}</p>
                    <p className="font-semibold text-slate-100">{result.place.noise_db_day} dB(A)</p>
                    <p className="text-xs text-slate-500">{t('ort.sonBase')}</p>
                  </div>
                  <div>
                    <p className="text-xs tracking-widest text-slate-500">{t('ort.oevGuete')}</p>
                    <p className="font-semibold text-slate-100">Klasse {result.place.oev_class}</p>
                    <p className="text-xs text-slate-500">{t('ort.oevDesc')}</p>
                  </div>
                  <div>
                    <p className="text-xs tracking-widest text-slate-500">{t('ort.gebaeude')}</p>
                    <p className="font-semibold text-slate-100">{result.place.gwr_building_count != null ? t('ort.gebaeudeUnit', {count: result.place.gwr_building_count}) : "—"}</p>
                  </div>
                </div>
              )}

              {tab === "planung" && (
                <div>
                  {result.baugesuche === undefined ? (
                    <p className="text-slate-400">{t('planung.loading')}</p>
                  ) : result.baugesuche.length === 0 ? (
                    <p className="text-slate-400">{t('planung.empty', {postcode: result.place.postcode})}</p>
                  ) : (
                    <>
                      <p className="mb-2 text-xs tracking-widest text-amber-300/80">
                        {t('planung.activeHeader', {count: result.baugesuche.length})}
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
                                  {b.municipality} · {t('planung.auflageBis', {date: b.auflage_end})} · {t('planung.daysLeft', {count: left, plural: left !== 1 ? 'e' : ''})} {urgent && <span className="font-semibold text-red-300">{t('planung.urgent')}</span>}
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
          {t('footer')}
        </p>
      </div>
    </main>
  );
}
