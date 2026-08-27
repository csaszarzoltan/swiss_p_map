"use client";

import { useEffect, useMemo, useState } from "react";
import dynamic from "next/dynamic";
import { useLocale, useTranslations } from "next-intl";
import SearchPanel from "../SearchPanel";
import LanguageSwitcher from "@/components/LanguageSwitcher";
import TopicSidebar, { type Topic } from "@/components/TopicSidebar";
import TopicList from "@/components/TopicList";
import DetailPanel from "@/components/DetailPanel";
import MapLegend from "@/components/MapLegend";
import WatchZone from "@/components/WatchZone";
import ShareButton from "@/components/ShareButton";
import type { Baugesuch, DistrictRepresentatives, PlaceInfo } from "@/lib/api";

const Map3D = dynamic(() => import("../Map3D"), { ssr: false });

interface Result {
  place?: PlaceInfo;
  politics?: DistrictRepresentatives;
  baugesuche?: Baugesuch[];
  error?: string;
  lngLat?: [number, number] | null;
}

export default function Home() {
  const t = useTranslations();
  const locale = useLocale();
  const [result, setResult] = useState<Result | null>(null);
  const [activeTopic, setActiveTopic] = useState<Topic>("overview");
  const [selectedId, setSelectedId] = useState<string | null>(null);
  const [aiSummary, setAiSummary] = useState<string | null>(null);

  const mapLocale = useMemo(
    () => ({
      title: t("map.title"),
      breadcrumb: t("map.breadcrumb"),
      subtitle: t("map.subtitle"),
      cantons: t("map.cantons"),
      population: t("map.population"),
      hint: t("map.hint"),
      compass: t("map.compass"),
      areaLabel: t("map.areaLabel"),
      popLabel: t("map.popLabel"),
      voteYes: t("map.voteYes"),
      voteNo: t("map.voteNo"),
      support: t("map.support"),
      cantonSubtitle: t("map.cantonSubtitle"),
      citySubtitle: t("map.citySubtitle"),
    }),
    [t],
  );

  const summary = useMemo(() => {
    if (!result?.place) return null;
    const p = result.place;
    const steuerLabel = p.steuerfuss_percent != null ? `${p.steuerfuss_percent}%` : t("summary.steuerFallback");
    const laerm = p.noise_db_day != null ? `${p.noise_db_day} dB` : t("summary.laermFallback");
    const oev = t("summary.oev", { klass: p.oev_class });
    const bg = result.baugesuche?.length
      ? result.baugesuche.length === 1
        ? t("summary.bgOne")
        : t("summary.bgMany", { count: result.baugesuche.length })
      : t("summary.bgNone");
    const pol =
      result.politics && result.politics.representatives.length > 0
        ? t("summary.polWith", { name: result.politics.representatives[0].name, party: result.politics.representatives[0].party, district: result.politics.district_name })
        : t("summary.polNone");
    try {
      return t("summary.template", { postcode: p.postcode, municipality: p.municipality, steuer: steuerLabel, laerm, oev, bg, pol });
    } catch {
      return `${p.postcode} ${p.municipality} — ${steuerLabel} · ${laerm} · ${oev} — ${bg} — ${pol}`;
    }
  }, [result, t]);

  const counts: Record<Topic, number> = useMemo(() => {
    if (!result?.place) return { overview: 0, politik: 0, ort: 0, planung: 0, solar: 0, oereb: 0 };
    return {
      overview: 1,
      politik: result.politics?.representatives.length ?? 0,
      ort: 6,
      planung: result.baugesuche?.length ?? 0,
      solar: result.place.solar_kwh_m2 != null ? 1 : 0,
      oereb: result.place.oereb_zone ? 1 : 0,
    };
  }, [result]);

  const handleResult = (r: Result) => {
    setResult(r);
    setActiveTopic("overview");
    setSelectedId(null);
    setAiSummary(null);
  };

  const handleTopicSelect = (topic: Topic) => {
    setActiveTopic(topic);
    setSelectedId(null);
  };

  useEffect(() => {
    if (!result?.place) return;
    const ctrl = new AbortController();
    const payload = {
      locale,
      postcode: result.place.postcode,
      place: result.place,
      politics: result.politics ?? {},
      baugesuche: result.baugesuche ?? [],
    };
    const base = process.env.NEXT_PUBLIC_API_URL ?? "http://127.0.0.1:8310";
    fetch(`${base}/api/v1/ai/summary`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
      signal: ctrl.signal,
    })
      .then((res) => (res.ok ? (res.json() as Promise<{ summary: string }>) : null))
      .then((data) => {
        if (data?.summary) setAiSummary(data.summary);
      })
      .catch(() => {});
    return () => ctrl.abort();
  }, [result, locale]);

  const selectedBaugesuch = selectedId ? (result?.baugesuche ?? []).find((b) => b.id === selectedId) : null;

  return (
    <main className="min-h-screen bg-[#030712] text-gray-100">
      {/* Fejléc Branding + Search + Nyelvválasztó */}
      <header className="border-b border-white/10 bg-[#0b1220]/90 backdrop-blur sticky top-0 z-30 shadow-[0_4px_20px_rgba(0,0,0,0.4)]">
        <div className="mx-auto flex max-w-[1280px] flex-col gap-3 px-4 py-3 sm:flex-row sm:items-center sm:justify-between sm:px-6">
          {/* Logo & Brand */}
          <div className="flex items-center gap-3">
            <div className="flex h-9 w-9 shrink-0 items-center justify-center rounded-lg bg-red-600 font-bold text-white shadow-md shadow-red-900/40">
              <span className="text-xl leading-none">✚</span>
            </div>
            <div>
              <div className="flex items-center gap-2">
                <span className="text-base font-bold tracking-tight text-white">{t("header.title")}</span>
                <span className="rounded bg-sky-500/20 px-1.5 py-0.5 text-[10px] font-semibold text-sky-400 border border-sky-500/30">v0.2.1</span>
              </div>
              <p className="text-[11px] text-slate-400 hidden sm:block">{t("header.subtitle")}</p>
            </div>
          </div>

          {/* Search + Language Switcher */}
          <div className="flex flex-col sm:flex-row items-stretch sm:items-center gap-3">
            <SearchPanel onResult={handleResult} />
            <div className="flex justify-end pt-1 sm:pt-0">
              <LanguageSwitcher />
            </div>
          </div>
        </div>
        {result?.error && (
          <div className="mx-auto max-w-[1280px] px-4 pb-3 sm:px-6">
            <p className="text-xs font-medium text-amber-400 bg-amber-500/10 border border-amber-500/20 rounded-md px-3 py-1.5 inline-block">
              {result.error}
            </p>
          </div>
        )}
      </header>

      {/* Menü fölül — teljes szélesség */}
      <div className="mx-auto max-w-[1280px]">
        <TopicSidebar activeTopic={activeTopic} onSelect={handleTopicSelect} counts={counts} />
      </div>

      {/* Térkép — teljes szélesség, a lehető legszélesebb */}
      <div className="mx-auto w-full max-w-[1600px]">
        <div className="relative"><Map3D
          selectedPostcode={result?.place?.postcode ?? null}
          baugesuche={activeTopic === "planung" && selectedBaugesuch ? [selectedBaugesuch] : (result?.baugesuche ?? [])}
          mapLocale={mapLocale}
        /><MapLegend activeTopic={activeTopic} /></div>
      </div>

      {/* Lista + Részletező — a térkép alatt */}
      <div className="mx-auto max-w-[1280px] border-t border-white/10 bg-[#080c18]">
        <TopicList topic={activeTopic} result={result} selectedId={selectedId} onSelect={setSelectedId} />
        <WatchZone center={result?.lngLat} radius={500} onRadiusChange={() => undefined} />
        <ShareButton getUrl={() => typeof window === "undefined" ? "" : window.location.href} />
        <DetailPanel topic={activeTopic} selectedId={selectedId} result={result} summary={summary} aiSummary={aiSummary} />
      </div>

      <p className="mx-auto max-w-[1280px] px-6 py-4 text-xs text-slate-600">{t("footer")}</p>
    </main>
  );
}
