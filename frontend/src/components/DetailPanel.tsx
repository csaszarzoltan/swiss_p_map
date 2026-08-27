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
      <div data-testid="detail-panel" className="border-t border-white/10 bg-[#0b1220]/60 p-4 text-sm text-slate-400">
        <p>{t("detail.hint")}</p>
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
    <div data-testid="detail-panel" className="border-t border-white/10 bg-[#0b1220]/80 p-4 backdrop-blur">
      {showOverview && (
        <div className="space-y-3">
          <p className="text-sm leading-relaxed text-slate-200">{aiSummary ?? summary}</p>
          <div className="grid grid-cols-2 gap-3 text-sm">
            <div className="rounded-lg border border-white/10 bg-white/[0.04] p-3">
              <SectionLabel>{t("overview.steuerfuss")}</SectionLabel>
              <p className="mt-1 font-semibold text-slate-100">{p.steuerfuss_percent}% · {p.municipality} ({p.canton})</p>
            </div>
            <div className="rounded-lg border border-white/10 bg-white/[0.04] p-3">
              <SectionLabel>{t("overview.laermOev")}</SectionLabel>
              <p className="mt-1 font-semibold text-slate-100">{p.noise_db_day} dB(A) · Klasse {p.oev_class}</p>
            </div>
          </div>
        </div>
      )}

      {showOrtDetail && (
        <div className="text-sm">
          {selectedId === "ort-steuer" && <><SectionLabel>{t("ort.steuerfuss")}</SectionLabel><p className="mt-1 text-slate-100">{p.steuerfuss_percent}% — {t("ort.gemeinde", { municipality: p.municipality, canton: p.canton })}</p></>}
          {selectedId === "ort-laerm" && <><SectionLabel>{t("ort.laermTag")}</SectionLabel><p className="mt-1 text-slate-100">{p.noise_db_day} dB(A) — {t("ort.sonBase")}</p></>}
          {selectedId === "ort-oev" && <><SectionLabel>{t("ort.oevGuete")}</SectionLabel><p className="mt-1 text-slate-100">Klasse {p.oev_class} — {t("ort.oevDesc")}</p></>}
          {selectedId === "ort-solar" && <><SectionLabel>{t("ort.solar")}</SectionLabel><p className="mt-1 text-slate-100">{p.solar_kwh_m2 != null ? `${p.solar_kwh_m2} kWh/m² · ${p.solar_class ?? ""}` : "—"}</p></>}
          {selectedId === "ort-oereb" && <><SectionLabel>{t("ort.oereb")}</SectionLabel><p className="mt-1 text-slate-100">{p.oereb_zone ?? "—"} — {t("ort.oerebDesc")}</p></>}
          {selectedId === "ort-gwr" && <><SectionLabel>{t("ort.gebaeude")}</SectionLabel><p className="mt-1 text-slate-100">{p.gwr_building_count ?? "—"}</p></>}
        </div>
      )}

      {showPolitikDetail && selectedRep && (
        <div className="text-sm">
          <SectionLabel>{selectedRep.wahlkreis} · {selectedRep.party}</SectionLabel>
          <p className="mt-1 text-lg font-bold text-slate-100">{selectedRep.name}</p>
          <p className="mt-1 text-xs text-slate-400">{t("politik.source")}</p>
        </div>
      )}

      {showPlanungDetail && selectedBaugesuch && (
        <div className="text-sm">
          <SectionLabel>{selectedBaugesuch.municipality} · {selectedBaugesuch.canton}</SectionLabel>
          <a href={selectedBaugesuch.source_url} target="_blank" rel="noreferrer" className="mt-1 block font-semibold text-sky-300 hover:underline">
            {selectedBaugesuch.title}
          </a>
          <p className="mt-1 text-xs text-slate-400">Aufl. {selectedBaugesuch.auflage_start} — {selectedBaugesuch.auflage_end} · {selectedBaugesuch.geocode_precision}</p>
        </div>
      )}

      {showSolarDetail && (
        <div className="text-sm">
          <SectionLabel>{t("ort.solar")}</SectionLabel>
          <p className="mt-1 font-semibold text-amber-300">{p.solar_kwh_m2 != null ? `${p.solar_kwh_m2} kWh/m²` : "—"} {p.solar_class ? `· ${p.solar_class}` : ""}</p>
          <p className="mt-1 text-xs text-slate-400">BFE Sonnendach · {t("ort.solarDesc", { kwh: String(p.solar_kwh_m2 ?? "—") })}</p>
        </div>
      )}

      {showOerebDetail && (
        <div className="text-sm">
          <SectionLabel>{t("ort.oereb")}</SectionLabel>
          <p className="mt-1 font-semibold text-purple-300">{p.oereb_zone ?? "—"}</p>
          <p className="mt-1 text-xs text-slate-400">{t("ort.oerebDesc")}</p>
        </div>
      )}

      {!showOverview && !showOrtDetail && !showPolitikDetail && !showPlanungDetail && !showSolarDetail && !showOerebDetail && (
        <p className="text-sm text-slate-400">{t("detail.selectHint")}</p>
      )}
    </div>
  );
}
