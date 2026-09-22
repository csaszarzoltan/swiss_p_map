"use client";

import { useEffect, useRef, useState } from "react";
import { useTranslations } from "next-intl";
import SourceTrustBadge from "../SourceTrustBadge";

type Status = "loading" | "ready" | "empty" | "error";
type Trust = "official_measurement" | "official_publication" | "modeled_estimate" | "stale" | "source_pending";

interface ForecastDay { date: string; temp_min_c: number; temp_max_c: number; precip_prob_pct: number; condition: string }
interface ForecastResp {
  postcode: string; current_temp_c: number; current_condition: string;
  observed_at: string; days: ForecastDay[]; source: string;
  trust_state: Trust; fetched_at: string; cache_ttl_seconds: number;
}
interface LiveListResp {
  status: Trust; items: unknown[]; source: string; official_url: string; fetched_at: string; note: string;
}

const API = process.env.NEXT_PUBLIC_API_URL ?? "http://127.0.0.1:8310";

function condEmoji(c: string): string {
  switch (c) {
    case "clear": return "☀️";
    case "mostly_clear": return "🌤️";
    case "partly_cloudy": return "⛅";
    case "overcast": return "☁️";
    case "fog": return "🌫️";
    case "drizzle": return "🌦️";
    case "rain": return "🌧️";
    case "snow": return "❄️";
    case "thunderstorm": return "⛈️";
    default: return "🌡️";
  }
}

function shortDay(iso: string, locale: string): string {
  try {
    return new Intl.DateTimeFormat(locale, { weekday: "short" }).format(new Date(`${iso}T12:00:00`));
  } catch { return iso.slice(5); }
}

export default function WeatherVisualWidget({ postcode = "8004" }: { postcode?: string }) {
  const t = useTranslations("phase3.feature052");
  const localeT = useTranslations();
  const [status, setStatus] = useState<Status>("loading");
  const [data, setData] = useState<ForecastResp | null>(null);
  const [trust, setTrust] = useState<Trust>("source_pending");
  const [meta, setMeta] = useState<{ source: string; at: string }>({ source: "", at: "" });
  const [alerts, setAlerts] = useState<LiveListResp | null>(null);
  const seq = useRef(0);

  useEffect(() => {
    const my = ++seq.current;
    const controller = new AbortController();
    setStatus("loading");
    setData(null);
    fetch(`${API}/api/v1/weather/forecast?postcode=${encodeURIComponent(postcode)}`, { signal: controller.signal })
      .then((r) => (r.ok ? r.json() : Promise.reject(new Error(String(r.status)))))
      .then((body: ForecastResp) => {
        if (seq.current !== my) return;
        setData(body);
        setTrust(body.trust_state ?? "modeled_estimate");
        setMeta({ source: body.source ?? "", at: body.fetched_at ?? body.observed_at ?? "" });
        setStatus(body.days?.length ? "ready" : "empty");
      })
      .catch((e: unknown) => {
        if (e instanceof DOMException && e.name === "AbortError") return;
        if (seq.current !== my) return;
        // Provider outage: surface stale/source_pending, never fake official data.
        setTrust("source_pending");
        setStatus("error");
      });
    fetch(`${API}/api/v1/weather/alerts?live=true`, { signal: controller.signal })
      .then((r) => (r.ok ? r.json() : Promise.reject(new Error(String(r.status)))))
      .then((body: LiveListResp) => { if (seq.current === my) setAlerts(body); })
      .catch(() => { /* alerts stay hidden on failure */ });
    return () => controller.abort();
  }, [postcode]);

  const locale = (() => { try { return String(localeT("locale" as never) ?? "de"); } catch { return "de"; } })();

  if (status === "loading")
    return (
      <article data-testid="weather-visual-widget" aria-live="polite" className="rounded-2xl border border-white/10 p-4">
        <h3 className="font-bold">{t("title")}</h3>
        <p className="mt-3 text-sm text-slate-400">{t("loading")}</p>
      </article>
    );

  if (status === "error")
    return (
      <article data-testid="weather-visual-widget" role="alert" className="rounded-2xl border border-white/10 p-4">
        <div className="flex items-center justify-between gap-2">
          <h3 className="font-bold">{t("title")}</h3>
          <SourceTrustBadge state="source_pending" source={meta.source || t("source")} refreshedAt={meta.at} />
        </div>
        <p className="mt-3 text-sm text-slate-300">{t("error")}</p>
        <p className="mt-1 text-xs text-slate-500">{t("errorHint")}</p>
      </article>
    );

  if (status === "empty" || !data)
    return (
      <article data-testid="weather-visual-widget" aria-live="polite" className="rounded-2xl border border-white/10 p-4">
        <h3 className="font-bold">{t("title")}</h3>
        <p className="mt-3 text-sm text-slate-400">{t("empty")}</p>
      </article>
    );

  const mins = data.days.map((d) => d.temp_min_c);
  const maxs = data.days.map((d) => d.temp_max_c);
  const lo = Math.min(...mins);
  const hi = Math.max(...maxs);
  const span = Math.max(1, hi - lo);

  return (
    <article data-testid="weather-visual-widget" aria-live="polite" className="rounded-2xl border border-white/10 p-4">
      <div className="flex items-center justify-between gap-2">
        <h3 className="font-bold">{t("title")} · {data.postcode}</h3>
        <SourceTrustBadge state={trust} source={meta.source} refreshedAt={meta.at} />
      </div>

      <div className="mt-3 flex items-baseline gap-2">
        <span className="text-3xl font-extrabold" aria-label={t("currentTemp", { v: Math.round(data.current_temp_c) })}>
          {condEmoji(data.current_condition)} {Math.round(data.current_temp_c)}°
        </span>
        <span className="text-xs text-slate-400">{t(`cond.${data.current_condition}`)}</span>
      </div>

      <ol className="mt-3 grid grid-cols-7 gap-1" aria-label={t("weekTrend")}>
        {data.days.map((d) => {
          const left = ((d.temp_min_c - lo) / span) * 100;
          const width = Math.max(8, ((d.temp_max_c - d.temp_min_c) / span) * 100);
          return (
            <li key={d.date} className="rounded bg-slate-800/80 p-1.5 text-center text-[11px] leading-tight">
              <div className="font-semibold text-slate-300">{shortDay(d.date, locale)}</div>
              <div className="text-base" role="img" aria-label={t(`cond.${d.condition}`)}>{condEmoji(d.condition)}</div>
              <div className="font-bold">{Math.round(d.temp_max_c)}°</div>
              <div className="text-slate-400">{Math.round(d.temp_min_c)}°</div>
              <div className="relative mt-1 h-1 rounded bg-slate-700" aria-hidden="true">
                <div className="absolute h-1 rounded bg-sky-400" style={{ left: `${left}%`, width: `${width}%` }} />
              </div>
              <div className="mt-1 text-sky-300" aria-label={t("precip", { v: d.precip_prob_pct })}>
                {d.precip_prob_pct > 0 ? `💧${d.precip_prob_pct}%` : "·"}
              </div>
            </li>
          );
        })}
      </ol>

      {alerts && alerts.status === "source_pending" ? (
        <p className="mt-3 rounded bg-slate-500/15 p-2 text-xs text-slate-300">
          {t("alertsPending")}{" "}
          <a className="underline" href={alerts.official_url} target="_blank" rel="noreferrer">{t("officialMap")}</a>
        </p>
      ) : null}
      <p className="mt-2 text-[11px] text-slate-500">
        {t("waterHint")}{" "}
        <a className="underline" href="https://www.hydrodaten.admin.ch" target="_blank" rel="noreferrer">{t("officialMap")}</a>
      </p>
    </article>
  );
}
