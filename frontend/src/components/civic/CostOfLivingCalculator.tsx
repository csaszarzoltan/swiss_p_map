"use client";

import { useEffect, useRef, useState } from "react";
import { useTranslations } from "next-intl";
import SourceTrustBadge from "../SourceTrustBadge";

type Status = "idle" | "loading" | "ready" | "empty" | "error";
type Trust = "official_measurement" | "official_publication" | "modeled_estimate" | "stale" | "source_pending";

interface CostResp {
  postcode: string;
  income_chf: number;
  size_m2: number;
  housing_chf: number;
  tax_chf: number;
  health_insurance_chf: number;
  commute_chf: number;
  total_monthly_chf: number;
  remaining_monthly_chf: number;
  trust_state: Trust;
  disclaimer: string;
  source: string;
  fetched_at: string;
}

const API = process.env.NEXT_PUBLIC_API_URL ?? "http://127.0.0.1:8310";

export default function CostOfLivingCalculator({ postcode }: { postcode: string }) {
  const t = useTranslations("phase3.feature054");
  const [income, setIncome] = useState(120000);
  const [size, setSize] = useState(80);
  const [status, setStatus] = useState<Status>("idle");
  const [data, setData] = useState<CostResp | null>(null);
  const seq = useRef(0);

  // Debounced live recalculation with last-request-wins + abort.
  useEffect(() => {
    const my = ++seq.current;
    const controller = new AbortController();
    const timer = setTimeout(() => {
      setStatus("loading");
      fetch(
        `${API}/api/v1/costs/assessment?postcode=${encodeURIComponent(postcode)}&income_chf=${income}&size_m2=${size}`,
        { signal: controller.signal },
      )
        .then((r) => (r.ok ? r.json() : Promise.reject(new Error(String(r.status)))))
        .then((body: CostResp) => {
          if (seq.current !== my) return;
          setData(body);
          setStatus(body.total_monthly_chf > 0 ? "ready" : "empty");
        })
        .catch((e: unknown) => {
          if (e instanceof DOMException && e.name === "AbortError") return;
          if (seq.current !== my) return;
          setData(null);
          setStatus("error");
        });
    }, 250);
    return () => {
      clearTimeout(timer);
      controller.abort();
    };
  }, [postcode, income, size]);

  const rows: Array<[string, number | null]> = data
    ? [
        [t("housing"), data.housing_chf],
        [t("tax"), data.tax_chf],
        [t("health"), data.health_insurance_chf],
        [t("commute"), data.commute_chf],
        [t("remaining"), data.remaining_monthly_chf],
      ]
    : [];

  return (
    <article data-testid="cost-of-living-calculator" aria-live="polite" className="rounded-2xl border border-white/10 p-4">
      <div className="flex items-center justify-between gap-2">
        <h3 className="font-bold">{t("title")}</h3>
        <SourceTrustBadge
          state={(data?.trust_state ?? "modeled_estimate") as "modeled_estimate"}
          source={data?.source ?? ""}
          refreshedAt={data?.fetched_at}
        />
      </div>

      <label className="mt-3 block text-xs text-slate-400">
        {t("income")}: CHF {income.toLocaleString("de-CH")}
        <input
          aria-label={t("income")}
          className="mt-1 w-full"
          type="range"
          min={40000}
          max={300000}
          step={5000}
          value={income}
          onChange={(e) => setIncome(+e.target.value)}
        />
      </label>
      <label className="mt-2 block text-xs text-slate-400">
        {t("size")}: {size} m²
        <input
          aria-label={t("size")}
          className="mt-1 w-full"
          type="range"
          min={30}
          max={200}
          value={size}
          onChange={(e) => setSize(+e.target.value)}
        />
      </label>

      {(status === "idle" || status === "loading") && !data && (
        <p className="mt-3 text-sm text-slate-400">{t("loading")}</p>
      )}

      {status === "error" && (
        <div role="alert" className="mt-3">
          <p className="text-sm text-rose-300">{t("error")}</p>
          <p className="mt-1 text-xs text-slate-500">{t("errorHint")}</p>
        </div>
      )}

      {status === "empty" && <p className="mt-3 text-sm text-slate-400">{t("empty")}</p>}

      {data && (status === "ready" || status === "loading") && (
        <div className="mt-3">
          <dl className="space-y-1 text-sm">
            {rows.map(([label, v]) => (
              <div key={label} className="flex items-baseline justify-between gap-2">
                <dt className="text-slate-400">{label}</dt>
                <dd className="font-semibold tabular-nums">CHF {Math.round(v ?? 0).toLocaleString("de-CH")}</dd>
              </div>
            ))}
          </dl>
          <p className="mt-2 border-t border-white/10 pt-2 text-base font-extrabold tabular-nums">
            {t("total")}: CHF {Math.round(data.total_monthly_chf).toLocaleString("de-CH")}
          </p>
          <p className="mt-2 rounded bg-amber-500/10 p-2 text-[11px] leading-4 text-amber-200/90">{data.disclaimer || t("disclaimer")}</p>
        </div>
      )}
    </article>
  );
}
