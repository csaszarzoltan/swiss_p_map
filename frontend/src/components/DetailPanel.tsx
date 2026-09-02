"use client";

import { useTranslations } from "next-intl";
import type { Baugesuch, DistrictRepresentatives, HazardAssessment, IsosAssessment, PlaceInfo, PropertyPriceAssessment, TaxComparison } from "@/lib/api";
import type { Topic } from "./TopicSidebar";
import StrategicP1P2Panel from "./StrategicP1P2Panel";

interface DetailPanelProps {
  topic: Topic;
  selectedId: string | null;
  result: { place?: PlaceInfo; politics?: DistrictRepresentatives; baugesuche?: Baugesuch[]; propertyPrices?: PropertyPriceAssessment; taxComparison?: TaxComparison; hazardAssessment?: HazardAssessment; isosAssessment?: IsosAssessment } | null;
  summary: string | null;
  aiSummary: string | null;
  strategicP1P2?: Record<string, Record<string, unknown>>;
}

function SectionLabel({ children }: { children: React.ReactNode }) {
  return <p className="text-[11px] font-semibold tracking-[0.14em] text-slate-500">{children}</p>;
}

export default function DetailPanel({ topic, selectedId, result, summary, aiSummary, strategicP1P2 }: DetailPanelProps) {
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
      <StrategicP1P2Panel data={strategicP1P2} topic={topic} />
      {(topic === "overview" || topic === "ort") && (result.propertyPrices || result.taxComparison || result.hazardAssessment || result.isosAssessment) && (
        <section data-testid="strategic-p0-panel" aria-label="Strategic location indicators" className="mb-5 grid gap-3 md:grid-cols-2 xl:grid-cols-4">
          {result.propertyPrices && (
            <article data-testid="property-price-card" className="rounded-xl border border-sky-500/30 bg-sky-950/20 p-4">
              <SectionLabel>IMMOBILIENPREISINDEX · {result.propertyPrices.reference_period}</SectionLabel>
              {result.propertyPrices.segments.map((segment) => (
                <div key={segment.segment} className="mt-2">
                  <div className="flex justify-between text-sm"><span>{segment.segment === "single_family_house" ? "Einfamilienhaus" : "Eigentumswohnung"}</span><strong>CHF {segment.average_price_chf_m2.toLocaleString()}/m²</strong></div>
                  <div className="mt-1 h-1.5 rounded bg-slate-800"><div className="h-full rounded bg-sky-400" style={{ width: `${Math.min(100, segment.quarterly_index / 1.5)}%` }} /></div>
                  <p className="mt-1 text-xs text-slate-400">Index {segment.quarterly_index} · 1J {segment.change_1y_percent}% · 5J {segment.change_5y_percent}%</p>
                </div>
              ))}
              <p className="mt-2 text-[10px] text-slate-500">{result.propertyPrices.source} · regionale Schätzung</p>
            </article>
          )}
          {result.taxComparison && (
            <article data-testid="tax-comparison-card" className="rounded-xl border border-emerald-500/30 bg-emerald-950/20 p-4">
              <SectionLabel>STEUERWETTBEWERB</SectionLabel>
              <p className="mt-2 text-2xl font-bold">#{result.taxComparison.selected.national_rank} <span className="text-sm font-normal text-slate-400">/ 26</span></p>
              <div className="mt-2 flex h-3 overflow-hidden rounded"><span className="w-1/3 bg-emerald-500" /><span className="w-1/3 bg-amber-400" /><span className="w-1/3 bg-rose-500" /></div>
              <p className="mt-2 text-sm">{result.taxComparison.selected.canton}: {result.taxComparison.selected.steuerfuss_percent}% · CH Ø {result.taxComparison.national_average_percent}%</p>
              <p className="mt-1 text-xs text-slate-400">Nachbarn: {result.taxComparison.neighboring_cantons.map((x) => `${x.canton} ${x.steuerfuss_percent}%`).join(" · ") || "—"}</p>
            </article>
          )}
          {result.hazardAssessment && (
            <article data-testid="hazard-card" className="rounded-xl border border-amber-500/30 bg-amber-950/20 p-4">
              <SectionLabel>NATURGEFAHREN · BAFU</SectionLabel>
              <p className={`mt-2 inline-flex rounded-full px-2 py-1 text-xs font-bold ${result.hazardAssessment.risk_level === "high" ? "bg-rose-500/30 text-rose-200" : result.hazardAssessment.risk_level === "medium" ? "bg-amber-500/30 text-amber-200" : "bg-emerald-500/30 text-emerald-200"}`}>{result.hazardAssessment.risk_level.toUpperCase()}</p>
              <ul className="mt-2 text-sm text-slate-300">{result.hazardAssessment.hazards.map((x) => <li key={x.hazard_type}>{x.hazard_type}: {x.risk_level}</li>)}</ul>
              <p className="mt-2 text-[10px] text-slate-500">{result.hazardAssessment.disclaimer}</p>
            </article>
          )}
          {result.isosAssessment && (
            <article data-testid="isos-card" className="rounded-xl border border-purple-500/30 bg-purple-950/20 p-4">
              <SectionLabel>ISOS DENKMALSCHUTZ</SectionLabel>
              <p className="mt-2 text-lg font-bold text-purple-200">{result.isosAssessment.protected ? `${result.isosAssessment.classification} · ${result.isosAssessment.site_name}` : "Kein Treffer"}</p>
              <p className="mt-1 text-sm text-slate-400">Verzögerungsrisiko: {result.isosAssessment.delay_risk}</p>
              <p className="mt-2 text-[10px] text-slate-500">{result.isosAssessment.source}</p>
            </article>
          )}
        </section>
      )}
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
