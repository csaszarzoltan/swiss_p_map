"use client";

import { useEffect, useRef, useState } from "react";
import { useTranslations } from "next-intl";
import SourceTrustBadge from "../SourceTrustBadge";
import type { VoteAnalysis, VoteProposalItem } from "@/lib/api";

type Status = "loading" | "ready" | "empty" | "error";

const API = process.env.NEXT_PUBLIC_API_URL ?? "http://127.0.0.1:8310";

export default function VotingVisualCard() {
  const t = useTranslations("phase3.feature051");
  const [status, setStatus] = useState<Status>("loading");
  const [proposals, setProposals] = useState<VoteProposalItem[]>([]);
  const [selectedId, setSelectedId] = useState<number | null>(null);
  const [analysis, setAnalysis] = useState<VoteAnalysis | null>(null);
  const [detailStatus, setDetailStatus] = useState<Status>("loading");
  const seq = useRef(0);

  useEffect(() => {
    const my = ++seq.current;
    const controller = new AbortController();
    setStatus("loading");
    fetch(`${API}/api/v1/votes/proposals`, { signal: controller.signal })
      .then((r) => (r.ok ? r.json() : Promise.reject(new Error(String(r.status)))))
      .then((data: { items?: VoteProposalItem[] }) => {
        if (seq.current !== my) return;
        const items = data.items ?? [];
        setProposals(items);
        setStatus(items.length ? "ready" : "empty");
        if (items.length && selectedId === null) setSelectedId(items[0].id);
      })
      .catch((e: unknown) => {
        if (e instanceof DOMException && e.name === "AbortError") return;
        if (seq.current !== my) return;
        setStatus("error");
      });
    return () => controller.abort();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  useEffect(() => {
    if (selectedId === null) return;
    const my = ++seq.current;
    const controller = new AbortController();
    setDetailStatus("loading");
    setAnalysis(null);
    fetch(`${API}/api/v1/votes/proposals/${selectedId}/analysis`, { signal: controller.signal })
      .then((r) => (r.ok ? r.json() : Promise.reject(new Error(String(r.status)))))
      .then((data: VoteAnalysis) => {
        if (seq.current !== my) return;
        setAnalysis(data);
        setDetailStatus("ready");
      })
      .catch((e: unknown) => {
        if (e instanceof DOMException && e.name === "AbortError") return;
        if (seq.current !== my) return;
        setDetailStatus("error");
      });
    return () => controller.abort();
  }, [selectedId]);

  if (status === "loading")
    return (
      <article data-testid="voting-visual-card" aria-live="polite" className="rounded-2xl border border-white/10 p-4">
        <h3 className="font-bold">{t("title")}</h3>
        <p className="mt-3 text-sm text-slate-400">{t("loading")}</p>
      </article>
    );

  if (status === "error")
    return (
      <article data-testid="voting-visual-card" role="alert" className="rounded-2xl border border-white/10 p-4">
        <h3 className="font-bold">{t("title")}</h3>
        <p className="mt-3 text-sm text-rose-300">{t("error")}</p>
      </article>
    );

  if (status === "empty" || proposals.length === 0)
    return (
      <article data-testid="voting-visual-card" className="rounded-2xl border border-white/10 p-4">
        <h3 className="font-bold">{t("title")}</h3>
        <p className="mt-3 text-sm text-slate-400">{t("empty")}</p>
      </article>
    );

  const poll = analysis?.polls?.[0] ?? null;
  const yesPct = poll?.yes_percent ?? analysis?.national_yes_percent ?? null;
  const barLabel =
    yesPct !== null ? t("yesShare", { pct: String(yesPct) }) : t("noPollData");
  const isFinal = analysis?.proposal.status === "final";
  const trustState = poll ? "modeled_estimate" : isFinal ? "official_publication" : "source_pending";

  return (
    <article data-testid="voting-visual-card" aria-labelledby="vvc-title" className="rounded-2xl border border-white/10 p-4">
      <div className="flex items-start justify-between gap-2">
        <h3 id="vvc-title" className="font-bold">{t("title")}</h3>
        <SourceTrustBadge state={trustState} source={analysis?.proposal.source ?? proposals[0]?.source ?? "Bundeskanzlei / BFS VoteInfo"} />
      </div>

      <label className="mt-3 block text-xs text-slate-400">
        {t("proposalLabel")}
        <select
          aria-label={t("proposalLabel")}
          className="mt-1 w-full rounded-lg border border-white/10 bg-slate-900 p-2 text-sm text-slate-100"
          value={selectedId ?? ""}
          onChange={(e) => setSelectedId(Number(e.target.value))}
        >
          {proposals.map((p) => (
            <option key={p.id} value={p.id}>
              {p.title} · {p.vote_date}
            </option>
          ))}
        </select>
      </label>

      {detailStatus === "loading" && (
        <p aria-live="polite" className="mt-3 text-sm text-slate-400">{t("loadingDetail")}</p>
      )}
      {detailStatus === "error" && (
        <p role="alert" className="mt-3 text-sm text-rose-300">{t("errorDetail")}</p>
      )}
      {detailStatus === "ready" && analysis && (
        <div className="mt-3">
          {yesPct !== null ? (
            <div>
              <div aria-label={barLabel} role="img" className="h-3 overflow-hidden rounded bg-rose-500">
                <div className="h-full bg-sky-500" style={{ width: `${Math.min(100, Math.max(0, yesPct))}%` }} />
              </div>
              <p className="mt-1 text-xs text-slate-400">{barLabel}</p>
            </div>
          ) : (
            <p className="text-xs text-slate-400">{t("noPollData")}</p>
          )}
          {poll && (
            <p className="mt-2 text-xs text-slate-500">
              {t("pollMeta", { institute: poll.institute, n: String(poll.sample_size), margin: String(poll.margin_percent) })}
            </p>
          )}
          {(analysis.national_yes_percent !== null || analysis.cantonal_yes_percent !== null || analysis.local_yes_percent !== null) && (
            <p className="mt-1 text-xs text-slate-500">
              {t("resultMeta", {
                nat: analysis.national_yes_percent !== null ? String(analysis.national_yes_percent) : "–",
                cant: analysis.cantonal_yes_percent !== null ? String(analysis.cantonal_yes_percent) : "–",
                loc: analysis.local_yes_percent !== null ? String(analysis.local_yes_percent) : "–",
              })}
            </p>
          )}
          <details className="mt-3">
            <summary className="cursor-pointer text-sm font-semibold">{t("proContra")}</summary>
            <div className="grid gap-3 text-sm md:grid-cols-2">
              <div>
                <p className="mt-2 font-semibold text-emerald-300">{t("pro")}</p>
                <ul className="mt-1 list-disc pl-5 text-slate-300">
                  {analysis.pro_arguments.map((a, i) => (
                    <li key={i}>{a}</li>
                  ))}
                </ul>
              </div>
              <div>
                <p className="mt-2 font-semibold text-rose-300">{t("contra")}</p>
                <ul className="mt-1 list-disc pl-5 text-slate-300">
                  {analysis.contra_arguments.map((a, i) => (
                    <li key={i}>{a}</li>
                  ))}
                </ul>
              </div>
            </div>
          </details>
        </div>
      )}
    </article>
  );
}
