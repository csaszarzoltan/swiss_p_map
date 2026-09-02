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
import RiskBadge from "@/components/RiskBadge";
import WatchZone from "@/components/WatchZone";
import ShareButton from "@/components/ShareButton";
import { parseShareableState, useShareableState } from "@/hooks/useShareableState";
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
  const [watchRadius, setWatchRadius] = useState<number>(500);

  // ADR-022: deep-link state ↔ URL (plz/topic/selected/radius)
  useShareableState(
    {
      plz: result?.place?.postcode,
      topic: activeTopic,
      selected: selectedId,
      radius: watchRadius,
    },
    (shared) => {
      if (shared.topic) setActiveTopic(shared.topic);
      if (shared.selected != null) setSelectedId(shared.selected);
      if (shared.radius) setWatchRadius(shared.radius);
    },
  );

  // ADR-022: restore search on mount if ?plz= is present
  const didRestoreRef = useState(() => ({ done: false }))[0];
  useEffect(() => {
    if (didRestoreRef.done) return;
    const parsed = parseShareableState(typeof window !== "undefined" ? window.location.search : "");
    if (parsed.plz) {
      didRestoreRef.done = true;
      const base = process.env.NEXT_PUBLIC_API_URL ?? "http://127.0.0.1:8310";
      Promise.all([
        fetch(`${base}/api/v1/place/${parsed.plz}?live=true`).then((r) => (r.ok ? r.json() : null)).catch(() => null) as Promise<PlaceInfo | null>,
        fetch(`${base}/api/v1/politics?postcode=${parsed.plz}&live=true`).then((r) => (r.ok ? r.json() : null)).catch(() => null) as Promise<DistrictRepresentatives | null>,
        fetch(`${base}/api/v1/planning/baugesuche?postcode=${parsed.plz}&active_only=true`).then((r) => (r.ok ? r.json() : null)).catch(() => null) as Promise<{ items: Baugesuch[] } | null>,
      ]).then(([place, politics, planning]) => {
        if (!place) return;
        void import("../postcode_coords").then((m) => {
          m.resolvePostcode(place.postcode).then((lngLat) => {
            setResult({ place, politics: politics ?? undefined, baugesuche: planning?.items ?? [], lngLat });
          });
        });
      });
      if (parsed.topic) setActiveTopic(parsed.topic);
      if (parsed.selected != null) setSelectedId(parsed.selected);
      if (parsed.radius) setWatchRadius(parsed.radius);
    }
  }, [didRestoreRef]);

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
    <main className="min-h-screen bg-[#030712] text-slate-100 selection:bg-sky-500 selection:text-white">
      {/* Floating Glassmorphic Header */}
      <header className="sticky top-0 z-40 border-b border-white/10 bg-slate-950/80 backdrop-blur-xl shadow-xl shadow-black/40">
        <div className="mx-auto flex max-w-[1440px] flex-col gap-3 px-4 py-3 sm:flex-row sm:items-center sm:justify-between sm:px-6">
          {/* Logo & Brand */}
          <div className="flex items-center gap-3">
            <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-xl bg-gradient-to-br from-red-500 to-red-700 font-bold text-white shadow-lg shadow-red-600/30 ring-1 ring-white/20">
              <span className="text-2xl leading-none">✚</span>
            </div>
            <div>
              <div className="flex items-center gap-2">
                <span className="text-base sm:text-lg font-extrabold tracking-tight text-white">{t("header.title")}</span>
                <span className="rounded-md bg-sky-500/20 px-2 py-0.5 text-[10px] font-bold text-sky-300 border border-sky-500/30 uppercase tracking-wider">v0.3 Swiss</span>
              </div>
              <p className="text-xs text-slate-400 hidden sm:block">{t("header.subtitle")}</p>
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
          <div className="mx-auto max-w-[1440px] px-4 pb-3 sm:px-6">
            <p className="text-xs font-semibold text-amber-300 bg-amber-500/15 border border-amber-500/30 rounded-xl px-3.5 py-2 inline-flex items-center gap-2">
              <span>⚠️</span>
              <span>{result.error}</span>
            </p>
          </div>
        )}
      </header>

      {/* Menü sáv — Glassmorphic Pill Bar */}
      <div className="sticky top-[65px] z-30 border-b border-white/5 bg-slate-950/70 backdrop-blur-lg">
        <div className="mx-auto max-w-[1440px]">
          <TopicSidebar activeTopic={activeTopic} onSelect={handleTopicSelect} counts={counts} />
        </div>
      </div>

      {/* 3D Térkép Konténer */}
      <div className="mx-auto w-full max-w-[1600px] px-2 sm:px-4 py-2 sm:py-3">
        <div className="relative overflow-hidden rounded-2xl sm:rounded-3xl border border-white/10 bg-slate-950/60 shadow-2xl shadow-black/80">
          <Map3D
            selectedPostcode={result?.place?.postcode ?? null}
            baugesuche={activeTopic === "planung" && selectedBaugesuch ? [selectedBaugesuch] : (result?.baugesuche ?? [])}
            mapLocale={mapLocale}
          />
          <MapLegend activeTopic={activeTopic} />
        </div>
      </div>

      {/* Lista + Részletező — Tiszta Swiss Card szekciók */}
      <div className="mx-auto max-w-[1440px] px-2 sm:px-4 py-3 space-y-4">
        {result?.place && (result.place.risk_level || result.place.risk_reason) && (
          <div className="rounded-2xl border border-white/10 bg-slate-900/60 p-3 backdrop-blur-md">
            <RiskBadge
              level={result.place.risk_level as "low" | "medium" | "high" | null}
              reason={result.place.risk_reason}
            />
          </div>
        )}

        {/* Fő információs kártya doboz */}
        <div className="overflow-hidden rounded-2xl sm:rounded-3xl border border-white/10 bg-slate-900/70 backdrop-blur-xl shadow-xl">
          <TopicList topic={activeTopic} result={result} selectedId={selectedId} onSelect={setSelectedId} />
          
          <div className="flex flex-wrap items-center justify-between gap-3 border-t border-white/10 bg-slate-950/50 p-3 sm:px-5">
            <WatchZone center={result?.lngLat} radius={watchRadius} onRadiusChange={setWatchRadius} />
            <ShareButton
              getUrl={() => {
                const u = new URL(window.location.href);
                if (result?.place?.postcode) u.searchParams.set("plz", result.place.postcode);
                u.searchParams.set("topic", activeTopic);
                if (selectedId) u.searchParams.set("selected", selectedId);
                if (watchRadius !== 500) u.searchParams.set("radius", String(watchRadius));
                return u.toString();
              }}
            />
          </div>

          <DetailPanel topic={activeTopic} selectedId={selectedId} result={result} summary={summary} aiSummary={aiSummary} />
        </div>
      </div>

      <footer className="mx-auto max-w-[1440px] px-6 py-6 text-center text-xs text-slate-500">
        <p>{t("footer")}</p>
      </footer>
    </main>
  );
}
