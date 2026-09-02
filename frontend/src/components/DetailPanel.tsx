"use client";

import { useTranslations } from "next-intl";
import type { Baugesuch, DistrictRepresentatives, PlaceInfo } from "@/lib/api";
import type { Topic } from "./TopicSidebar";

interface DetailPanelProps {
  topic: Topic;
  selectedId: string | null;
  result: { place?: PlaceInfo; politics?: DistrictRepresentatives; baugesuche?: Baugesuch[] } | null;
  summary: string | null;
  aiSummary: string | null;
}

function SectionLabel({ children }: { children: React.ReactNode }) {
  return <p className="text-[11px] font-semibold tracking-[0.14em] text-slate-500">{children}</p>;
}

export default function DetailPanel({ topic, selectedId, result, summary, aiSummary }: DetailPanelProps) {
  const t = useTranslations();

  if (!result?.place) {
    return (
      <div data-testid="detail-panel" className="border-t border-white/10 bg-slate-950/60 p-6 text-center text-sm text-slate-400">
        <p className="flex items-center justify-center gap-2">
          <span>🔍</span>
          <span>{t("detail.hint")}</span>
        </p>
      </div>
    );
  }

  const p = result.place;
  const selectedBaugesuch = selectedId ? (result.baugesuche ?? []).find((b) => b.id === selectedId) : null;
  const selectedRep = selectedId ? (result.politics?.representatives ?? []).find((r) => r.id === selectedId) : null;

  const showOverview = topic === "overview" && !selectedId;
  const showOrtDetail = topic === "ort" && selectedId;
  const showPolitikDetail = topic === "politik" && selectedRep;
  const showPlanungDetail = topic === "planung" && selectedBaugesuch;
  const showSolarDetail = topic === "solar";
  const showOerebDetail = topic === "oereb";

  return (
    <div data-testid="detail-panel" className="border-t border-white/10 bg-slate-950/80 p-5 backdrop-blur-xl">
      {showOverview && (
        <div className="space-y-4">
          {/* AI Executive Summary Card */}
          <div className="relative overflow-hidden rounded-2xl border border-sky-500/30 bg-gradient-to-br from-slate-900/90 to-sky-950/40 p-4 shadow-lg shadow-sky-950/30">
            <div className="flex items-center gap-2 mb-2">
              <span className="flex h-5 w-5 items-center justify-center rounded-full bg-sky-500/20 text-xs text-sky-300">✦</span>
              <p className="text-xs font-bold uppercase tracking-wider text-sky-400">AI Executive Summary</p>
            </div>
            <p className="text-sm leading-relaxed text-slate-200">{aiSummary ?? summary}</p>
          </div>

          {/* 4 Swiss Key Metrics Grid */}
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
            {/* 1. Steuerfuss */}
            <div className="rounded-xl border border-white/10 bg-white/[0.03] p-3.5 transition hover:border-white/20">
              <SectionLabel>{t("overview.steuerfuss")}</SectionLabel>
              <div className="mt-1 flex items-baseline gap-1">
                <span className="text-2xl font-black tracking-tight text-white">{p.steuerfuss_percent ?? "—"}</span>
                <span className="text-xs font-semibold text-slate-400">%</span>
              </div>
              <p className="mt-0.5 text-[11px] text-slate-400 truncate">{p.municipality} ({p.canton})</p>
            </div>

            {/* 2. Lärm */}
            <div className="rounded-xl border border-white/10 bg-white/[0.03] p-3.5 transition hover:border-white/20">
              <SectionLabel>{t("ort.laermTag")}</SectionLabel>
              <div className="mt-1 flex items-baseline gap-1">
                <span className="text-2xl font-black tracking-tight text-sky-300">{p.noise_db_day ?? "—"}</span>
                <span className="text-xs font-semibold text-slate-400">dB(A)</span>
              </div>
              <p className="mt-0.5 text-[11px] text-slate-400">{t("ort.sonBase")}</p>
            </div>

            {/* 3. ÖV-Güte */}
            <div className="rounded-xl border border-white/10 bg-white/[0.03] p-3.5 transition hover:border-white/20">
              <SectionLabel>{t("ort.oevGuete")}</SectionLabel>
              <div className="mt-1 flex items-baseline gap-1">
                <span className="text-2xl font-black tracking-tight text-emerald-400">{p.oev_class}</span>
                <span className="text-xs font-semibold text-slate-400">ARE</span>
              </div>
              <p className="mt-0.5 text-[11px] text-slate-400">{t("ort.oevDesc")}</p>
            </div>

            {/* 4. Sonnendach */}
            <div className="rounded-xl border border-white/10 bg-white/[0.03] p-3.5 transition hover:border-white/20">
              <SectionLabel>{t("ort.solar")}</SectionLabel>
              <div className="mt-1 flex items-baseline gap-1">
                <span className="text-2xl font-black tracking-tight text-amber-300">{p.solar_kwh_m2 ?? "—"}</span>
                <span className="text-xs font-semibold text-slate-400">kWh/m²</span>
              </div>
              <p className="mt-0.5 text-[11px] text-amber-400/80 truncate">{p.solar_class ?? "BFE Sonnendach"}</p>
            </div>
          </div>
        </div>
      )}

      {showOrtDetail && (
        <div className="rounded-xl border border-white/10 bg-white/[0.03] p-4">
          {selectedId === "ort-steuer" && (
            <div>
              <SectionLabel>{t("ort.steuerfuss")}</SectionLabel>
              <p className="mt-1 text-2xl font-black text-white">{p.steuerfuss_percent}%</p>
              <p className="mt-1 text-xs text-slate-400">{t("ort.gemeinde", { municipality: p.municipality, canton: p.canton })} · {p.steuerfuss_source}</p>
            </div>
          )}
          {selectedId === "ort-laerm" && (
            <div>
              <SectionLabel>{t("ort.laermTag")}</SectionLabel>
              <p className="mt-1 text-2xl font-black text-sky-300">{p.noise_db_day} dB(A)</p>
              <p className="mt-1 text-xs text-slate-400">{t("ort.sonBase")} · BAFU Strassenlärm</p>
            </div>
          )}
          {selectedId === "ort-oev" && (
            <div>
              <SectionLabel>{t("ort.oevGuete")}</SectionLabel>
              <p className="mt-1 text-2xl font-black text-emerald-400">Klasse {p.oev_class}</p>
              <p className="mt-1 text-xs text-slate-400">{t("ort.oevDesc")} · ARE Bundesamt für Raumentwicklung</p>
            </div>
          )}
          {selectedId === "ort-solar" && (
            <div>
              <SectionLabel>{t("ort.solar")}</SectionLabel>
              <p className="mt-1 text-2xl font-black text-amber-300">{p.solar_kwh_m2 != null ? `${p.solar_kwh_m2} kWh/m²` : "—"}</p>
              <p className="mt-1 text-xs text-slate-400">{p.solar_class ?? ""} · BFE Sonnendach Schweiz</p>
            </div>
          )}
          {selectedId === "ort-oereb" && (
            <div>
              <SectionLabel>{t("ort.oereb")}</SectionLabel>
              <p className="mt-1 text-xl font-bold text-purple-300">{p.oereb_zone ?? "—"}</p>
              <p className="mt-1 text-xs text-slate-400">{t("ort.oerebDesc")} · Kataster der öffentlich-rechtlichen Eigentumsbeschränkungen</p>
            </div>
          )}
          {selectedId === "ort-gwr" && (
            <div>
              <SectionLabel>{t("ort.gebaeude")}</SectionLabel>
              <p className="mt-1 text-2xl font-black text-white">{p.gwr_building_count ?? "—"}</p>
              <p className="mt-1 text-xs text-slate-400">Eidgenössisches Gebäude- und Wohnungsregister (GWR)</p>
            </div>
          )}
        </div>
      )}

      {showPolitikDetail && selectedRep && (
        <div className="rounded-xl border border-white/10 bg-white/[0.03] p-4">
          <SectionLabel>{selectedRep.wahlkreis} · {selectedRep.party}</SectionLabel>
          <p className="mt-1 text-xl font-bold text-white">{selectedRep.name}</p>
          <p className="mt-1 text-xs text-slate-400">{t("politik.source")} · PARIS Parlamentsinformationssystem</p>
        </div>
      )}

      {showPlanungDetail && selectedBaugesuch && (
        <div className="rounded-xl border border-white/10 bg-white/[0.03] p-4">
          <div className="flex flex-wrap items-center justify-between gap-2">
            <SectionLabel>{selectedBaugesuch.municipality} · {selectedBaugesuch.canton}</SectionLabel>
            {selectedBaugesuch.risk_level && (
              <span className={`rounded-full px-2.5 py-0.5 text-[10px] font-bold uppercase tracking-wider ${
                selectedBaugesuch.risk_level === "high" ? "bg-red-500/20 text-red-300 border border-red-500/30" :
                selectedBaugesuch.risk_level === "medium" ? "bg-amber-500/20 text-amber-300 border border-amber-500/30" :
                "bg-emerald-500/20 text-emerald-300 border border-emerald-500/30"
              }`}>
                {selectedBaugesuch.risk_level} Risk
              </span>
            )}
          </div>
          <a href={selectedBaugesuch.source_url} target="_blank" rel="noreferrer" className="mt-2 block text-base font-bold text-sky-300 hover:underline">
            {selectedBaugesuch.title}
          </a>
          <div className="mt-3 grid grid-cols-2 sm:grid-cols-4 gap-2 text-xs">
            <div className="rounded bg-slate-900/60 p-2 border border-white/5">
              <span className="text-slate-500 block text-[10px] uppercase">Auflagefrist</span>
              <span className="text-slate-200 font-medium">{selectedBaugesuch.auflage_start} — {selectedBaugesuch.auflage_end}</span>
            </div>
            {selectedBaugesuch.contractor && (
              <div className="rounded bg-slate-900/60 p-2 border border-white/5">
                <span className="text-slate-500 block text-[10px] uppercase">Bauherrschaft</span>
                <span className="text-slate-200 font-medium truncate block">{selectedBaugesuch.contractor}</span>
              </div>
            )}
            {selectedBaugesuch.architect && (
              <div className="rounded bg-slate-900/60 p-2 border border-white/5">
                <span className="text-slate-500 block text-[10px] uppercase">Architekt</span>
                <span className="text-slate-200 font-medium truncate block">{selectedBaugesuch.architect}</span>
              </div>
            )}
            {selectedBaugesuch.zone_type && (
              <div className="rounded bg-slate-900/60 p-2 border border-white/5">
                <span className="text-slate-500 block text-[10px] uppercase">Zone</span>
                <span className="text-slate-200 font-medium">{selectedBaugesuch.zone_type}</span>
              </div>
            )}
          </div>
        </div>
      )}

      {showSolarDetail && (
        <div className="rounded-xl border border-white/10 bg-white/[0.03] p-4">
          <SectionLabel>{t("ort.solar")}</SectionLabel>
          <p className="mt-1 text-2xl font-black text-amber-300">{p.solar_kwh_m2 != null ? `${p.solar_kwh_m2} kWh/m²` : "—"} {p.solar_class ? `· ${p.solar_class}` : ""}</p>
          <p className="mt-1 text-xs text-slate-400">BFE Sonnendach · {t("ort.solarDesc", { kwh: String(p.solar_kwh_m2 ?? "—") })}</p>
        </div>
      )}

      {showOerebDetail && (
        <div className="rounded-xl border border-white/10 bg-white/[0.03] p-4">
          <SectionLabel>{t("ort.oereb")}</SectionLabel>
          <p className="mt-1 text-xl font-bold text-purple-300">{p.oereb_zone ?? "—"}</p>
          <p className="mt-1 text-xs text-slate-400">{t("ort.oerebDesc")}</p>
        </div>
      )}

      {!showOverview && !showOrtDetail && !showPolitikDetail && !showPlanungDetail && !showSolarDetail && !showOerebDetail && (
        <p className="text-sm text-slate-400">{t("detail.selectHint")}</p>
      )}
    </div>
  );
}
