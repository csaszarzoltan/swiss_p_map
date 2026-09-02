"use client";

import { useTranslations } from "next-intl";
import type { Baugesuch, DistrictRepresentatives, PlaceInfo } from "@/lib/api";
import type { Topic } from "./TopicSidebar";

interface TopicListProps {
  topic: Topic;
  result: { place?: PlaceInfo; politics?: DistrictRepresentatives; baugesuche?: Baugesuch[] } | null;
  selectedId: string | null;
  onSelect: (id: string) => void;
}

export default function TopicList({ topic, result, selectedId, onSelect }: TopicListProps) {
  const t = useTranslations();

  if (!result?.place) {
    return (
      <div data-testid="topic-list" className="p-4 text-sm text-slate-400">
        <p>{t("list.noSelection")}</p>
      </div>
    );
  }

  const items: { id: string; label: string; sublabel?: string }[] = [];

  if (topic === "politik" && result.politics) {
    for (const r of result.politics.representatives) {
      items.push({ id: r.id, label: r.name, sublabel: `${r.party} · ${r.wahlkreis}` });
    }
  } else if (topic === "ort") {
    const p = result.place;
    items.push(
      { id: "ort-steuer", label: t("ort.steuerfuss"), sublabel: p.steuerfuss_percent != null ? `${p.steuerfuss_percent}% · ${p.municipality}` : "—" },
      { id: "ort-laerm", label: t("ort.laermTag"), sublabel: p.noise_db_day != null ? `${p.noise_db_day} dB(A)` : "—" },
      { id: "ort-oev", label: t("ort.oevGuete"), sublabel: `Klasse ${p.oev_class}` },
      { id: "ort-solar", label: t("ort.solar"), sublabel: p.solar_kwh_m2 != null ? `${p.solar_kwh_m2} kWh/m² (${p.solar_class ?? ""})` : "—" },
      { id: "ort-oereb", label: t("ort.oereb"), sublabel: p.oereb_zone ?? "—" },
      { id: "ort-gwr", label: t("ort.gebaeude"), sublabel: p.gwr_building_count != null ? `${p.gwr_building_count}` : "—" },
    );
  } else if (topic === "planung") {
    for (const b of (result.baugesuche ?? []).slice(0, 12)) {
      items.push({ id: b.id, label: b.title.slice(0, 80), sublabel: `${b.municipality} · ${b.auflage_end}` });
    }
    if (items.length === 0) items.push({ id: "planung-empty", label: t("planung.empty", { postcode: result.place.postcode }) });
  } else if (topic === "solar") {
    const p = result.place;
    items.push({ id: "solar-main", label: t("ort.solar"), sublabel: p.solar_kwh_m2 != null ? `${p.solar_kwh_m2} kWh/m² · ${p.solar_class ?? ""}` : t("summary.laermFallback") });
  } else if (topic === "oereb") {
    items.push({ id: "oereb-main", label: t("ort.oereb"), sublabel: result.place.oereb_zone ?? "—" });
  } else {
    items.push({ id: "overview-summary", label: t("tabs.overview"), sublabel: `${result.place.postcode} ${result.place.municipality}` });
    if (result.politics) items.push({ id: "overview-politik", label: t("tabs.politik"), sublabel: result.politics.district_name });
  }

  return (
    <div data-testid="topic-list" className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-2 p-3">
      {items.map((it) => {
        const isSelected = selectedId === it.id;
        return (
          <button
            key={it.id}
            data-testid={`list-item-${it.id}`}
            onClick={() => onSelect(it.id)}
            className={`group flex flex-col justify-between rounded-xl border p-3 text-left transition-all duration-200 ${
              isSelected
                ? "border-sky-400 bg-sky-500/20 text-white shadow-md shadow-sky-500/20 ring-1 ring-sky-400/40"
                : "border-white/10 bg-slate-900/60 text-slate-200 hover:border-white/20 hover:bg-slate-800/80"
            }`}
          >
            <p className="line-clamp-2 text-sm font-semibold leading-snug group-hover:text-sky-300 transition-colors">{it.label}</p>
            {it.sublabel && <p className="mt-1 line-clamp-1 text-xs text-slate-400 font-medium">{it.sublabel}</p>}
          </button>
        );
      })}
    </div>
  );
}
