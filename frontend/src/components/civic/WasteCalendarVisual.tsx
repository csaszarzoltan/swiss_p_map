"use client";

import { useEffect, useRef, useState } from "react";
import { useLocale, useTranslations } from "next-intl";
import SourceTrustBadge from "../SourceTrustBadge";

type Status = "loading" | "ready" | "empty" | "error";
type Trust = "official_measurement" | "official_publication" | "modeled_estimate" | "cadastral_registry" | "stale" | "source_pending";

interface WasteEvent { waste_type: string; collection_date: string; days_until: number }
interface WasteResp {
  postcode: string; events: WasteEvent[]; source: string;
  source_url: string; fetched_at: string; trust_state: Trust;
}

const API = process.env.NEXT_PUBLIC_API_URL ?? "http://127.0.0.1:8310";

function fmtDate(iso: string, locale: string): string {
  try {
    return new Intl.DateTimeFormat(locale, { weekday: "short", day: "numeric", month: "numeric" }).format(new Date(`${iso}T12:00:00`));
  } catch { return iso; }
}

export default function WasteCalendarVisual({ postcode = "8004" }: { postcode?: string }) {
  const t = useTranslations("phase3.feature053");
  const locale = useLocale();
  const [status, setStatus] = useState<Status>("loading");
  const [data, setData] = useState<WasteResp | null>(null);
  const seq = useRef(0);

  useEffect(() => {
    const my = ++seq.current;
    const controller = new AbortController();
    setStatus("loading");
    setData(null);
    fetch(`${API}/api/v1/municipal/waste-calendar?postcode=${encodeURIComponent(postcode)}`, { signal: controller.signal })
      .then((r) => (r.ok ? r.json() : Promise.reject(new Error(String(r.status)))))
      .then((body: WasteResp) => {
        if (seq.current !== my) return;
        setData(body);
        setStatus(body.events?.length ? "ready" : "empty");
      })
      .catch((e: unknown) => {
        if (e instanceof DOMException && e.name === "AbortError") return;
        if (seq.current !== my) return;
        setStatus("error");
      });
    return () => controller.abort();
  }, [postcode]);

  if (status === "loading")
    return (
      <article data-testid="waste-calendar-visual" aria-live="polite" className="rounded-2xl border border-white/10 p-4">
        <h3 className="font-bold">{t("title")}</h3>
        <p className="mt-3 text-sm text-slate-400">{t("loading")}</p>
      </article>
    );

  if (status === "error")
    return (
      <article data-testid="waste-calendar-visual" role="alert" className="rounded-2xl border border-white/10 p-4">
        <h3 className="font-bold">{t("title")}</h3>
        <p className="mt-3 text-sm text-rose-300">{t("error")}</p>
      </article>
    );

  if (status === "empty" || !data)
    return (
      <article data-testid="waste-calendar-visual" className="rounded-2xl border border-white/10 p-4">
        <h3 className="font-bold">{t("title")}</h3>
        <p className="mt-3 text-sm text-slate-400">{t("empty")}</p>
      </article>
    );

  const icsUrl = `${API}/api/v1/municipal/waste-calendar.ics?postcode=${encodeURIComponent(data.postcode)}`;

  return (
    <article data-testid="waste-calendar-visual" aria-live="polite" className="rounded-2xl border border-white/10 p-4">
      <div className="flex items-center justify-between gap-2">
        <h3 className="font-bold">{t("title")} · {data.postcode}</h3>
        <SourceTrustBadge state={data.trust_state} source={data.source} refreshedAt={data.fetched_at} />
      </div>
      <ol className="mt-3 space-y-1.5" aria-label={t("listLabel")}>
        {data.events.map((e) => (
          <li key={`${e.waste_type}-${e.collection_date}`} className="flex items-baseline justify-between gap-2 rounded bg-slate-800/80 px-2 py-1.5 text-sm">
            <span className="font-semibold">♻ {e.waste_type} <span className="font-normal text-slate-400">· {fmtDate(e.collection_date, locale)}</span></span>
            <span className="shrink-0 text-xs text-emerald-300">
              {e.days_until === 0 ? t("today") : e.days_until === 1 ? t("tomorrow") : t("inDays", { n: e.days_until })}
            </span>
          </li>
        ))}
      </ol>
      <a href={icsUrl} download={`abfall-${data.postcode}.ics`} className="mt-3 inline-block rounded bg-emerald-600 px-3 py-2 text-sm font-semibold text-white hover:bg-emerald-500">
        {t("exportIcs")}
      </a>
    </article>
  );
}
