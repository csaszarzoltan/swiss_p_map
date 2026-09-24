"use client";

/**
 * ADR-023/B: Watch-zone notification UI (events + Einsprachefrist countdown).
 *
 * Traceability:
 * - REQ-A1: notifications only for a user-declared zone *with* consent -> the
 *   submit button stays disabled and the reason is programmatically available.
 * - REQ-A2: dedup lives on the server; the UI never invents a second event.
 * - REQ-A3: every event renders source + fetched_at + trust_state through
 *   SourceTrustBadge (no unsourced claim).
 * - REQ-B1/B2: `state` comes from the backend and is *tightened* client-side —
 *   a negative days_left can never be displayed as `open`.
 * - REQ-B3: the disclaimer sits inside the deadline row, next to the countdown.
 */

import { useCallback, useEffect, useMemo, useRef, useState } from "react";
import { useTranslations } from "next-intl";
import SourceTrustBadge from "./SourceTrustBadge";
import { coordFor } from "@/app/postcode_coords";
import {
  createWatchZone,
  fetchWatchDeadlines,
  fetchWatchEvents,
  type WatchChannel,
  type WatchDeadlineItem,
  type WatchDeadlineState,
  type WatchEventItem,
  type WatchEventsResponse,
  type WatchDeadlinesResponse,
  type WatchTrustState,
  type WatchZoneRequest,
} from "@/lib/api";

export type WatchFetchStatus = "loading" | "ready" | "empty" | "error";
export type SubFetchStatus = "success" | "source_pending" | "error";

export const DEFAULT_RADIUS_M = 500;

/** Berlin/amber/rose tones: state is readable without relying on colour alone. */
export function deadlineTone(state: WatchDeadlineState): string {
  if (state === "expired") return "bg-rose-500/20 text-rose-200 border border-rose-500/40";
  if (state === "due_soon") return "bg-amber-500/20 text-amber-200 border border-amber-500/40";
  return "bg-sky-500/20 text-sky-200 border border-sky-500/40";
}

/**
 * REQ-B2 (client-side hardening): a deadline that is already past must never be
 * rendered as open, whatever the payload claims.
 */
export function effectiveState(item: { state: WatchDeadlineState; days_left: number }): WatchDeadlineState {
  if (item.days_left < 0) return "expired";
  if (item.days_left <= 3) return "due_soon";
  return item.state === "expired" ? "expired" : item.state;
}

export interface ZoneFormInput {
  postcode: string;
  channels: WatchChannel[];
  consent: boolean;
  email?: string;
  subscriptionEndpoint?: string;
  radiusM?: number;
  zoneId?: string;
}

export type ZoneBuildResult =
  | { ok: true; request: WatchZoneRequest }
  | { ok: false; error: "consentRequired" | "noChannel" | "emailRequired" | "pushRequired" | "postcodeRequired" };

/**
 * REQ-A1 gate: no zone is ever submitted without consent and a real delivery
 * target. Returns a translatable error key instead of guessing a default.
 */
export function buildZoneRequest(input: ZoneFormInput): ZoneBuildResult {
  if (!input.postcode) return { ok: false, error: "postcodeRequired" };
  if (!input.consent) return { ok: false, error: "consentRequired" };
  const channels = input.channels ?? [];
  if (channels.length === 0) return { ok: false, error: "noChannel" };
  if (channels.includes("email") && !(input.email ?? "").trim()) return { ok: false, error: "emailRequired" };
  if (channels.includes("push") && !(input.subscriptionEndpoint ?? "").trim()) return { ok: false, error: "pushRequired" };
  const center = coordFor(input.postcode);
  const request: WatchZoneRequest = {
    zone_id: input.zoneId ?? `zone-${input.postcode}`,
    postcode: input.postcode,
    radius_m: input.radiusM ?? DEFAULT_RADIUS_M,
    channels,
    consent: true,
  };
  if (center) {
    request.lon = center[0];
    request.lat = center[1];
  }
  const email = (input.email ?? "").trim();
  if (channels.includes("email") && email) request.email = email;
  const endpoint = (input.subscriptionEndpoint ?? "").trim();
  if (channels.includes("push") && endpoint) request.subscription_endpoint = endpoint;
  return { ok: true, request };
}

/** Events of the active place only — a foreign postcode is never shown as ours. */
export function toViewData(
  deadlines: WatchDeadlinesResponse | null,
  events: WatchEventsResponse | null,
  postcode: string,
  error?: boolean
): {
  status: WatchFetchStatus;
  events: WatchEventItem[];
  deadlines: WatchDeadlineItem[];
  eventsStatus: SubFetchStatus;
  deadlinesStatus: SubFetchStatus;
  fetchedAt: string;
} {
  const ownEvents = (events?.items ?? []).filter((e) => e.postcode === postcode);
  const ownDeadlines = (deadlines?.items ?? []).filter((d) => !d.postcode || d.postcode === postcode);
  const eventsStatus: SubFetchStatus = events ? (events.status === "success" ? "success" : "source_pending") : "error";
  const deadlinesStatus: SubFetchStatus = deadlines
    ? deadlines.status === "success"
      ? "success"
      : "source_pending"
    : "error";
  let status: WatchFetchStatus = "ready";
  if (!events && !deadlines) status = "error";
  else if (ownEvents.length === 0 && ownDeadlines.length === 0) status = "empty";
  else if (error) status = "error";
  return {
    status,
    events: ownEvents,
    deadlines: ownDeadlines,
    eventsStatus,
    deadlinesStatus,
    fetchedAt: events?.fetched_at || deadlines?.fetched_at || "",
  };
}

export interface WatchEventsViewProps {
  status: WatchFetchStatus;
  events: WatchEventItem[];
  deadlines: WatchDeadlineItem[];
  eventsStatus?: SubFetchStatus;
  deadlinesStatus?: SubFetchStatus;
  postcode?: string;
  fetchedAt?: string;
  source?: string;
  trustState?: WatchTrustState;
  rule?: string;
  consent?: boolean;
  channels?: WatchChannel[];
  email?: string;
  subscriptionEndpoint?: string;
  consentReason?: ZoneBuildResult | null;
  submitMessage?: { ok: boolean; text: string } | null;
  onToggleChannel?: (channel: WatchChannel) => void;
  onConsentChange?: (value: boolean) => void;
  onEmailChange?: (value: string) => void;
  onSubscriptionEndpointChange?: (value: string) => void;
  onSubmit?: () => void;
}

function Countdown({ item, t }: { item: WatchDeadlineItem; t: (key: string, values?: Record<string, string | number>) => string }) {
  const state = effectiveState(item);
  if (state === "expired") return <>{t("expiredAgo", { n: Math.abs(item.days_left) })}</>;
  if (item.days_left === 0) return <>{t("dueToday")}</>;
  return <>{t("daysLeft", { n: item.days_left })}</>;
}

/** Pure presentational view: no hooks beyond i18n, so it is testable in-process. */
export function WatchEventsView(props: WatchEventsViewProps) {
  const t = useTranslations("resident.feature023");
  const {
    status,
    events,
    deadlines,
    eventsStatus = "success",
    deadlinesStatus = "success",
    postcode,
    fetchedAt,
    source,
    trustState,
    rule,
    consent = false,
    channels = ["email"],
    email = "",
    subscriptionEndpoint = "",
    consentReason,
    submitMessage,
    onToggleChannel,
    onConsentChange,
    onEmailChange,
    onSubscriptionEndpointChange,
    onSubmit,
  } = props;
  const stateLabel = (s: WatchDeadlineState) =>
    s === "expired" ? t("stateExpired") : s === "due_soon" ? t("stateDueSoon") : t("stateOpen");
  const reasonText = consentReason && !consentReason.ok ? t(consentReason.error) : "";

  return (
    <article data-testid="watch-events-card" data-postcode={postcode || undefined} aria-label={postcode ? `${t("title")} · ${postcode}` : t("title")} aria-live="polite" className="mt-4 rounded-2xl border border-white/10 bg-slate-900/60 p-4">
      <div className="flex flex-wrap items-center justify-between gap-2">
        <h3 className="font-bold">{t("title")}</h3>
        <span className="flex items-center gap-2">
          {source && <SourceTrustBadge state={trustState ?? "official_publication"} source={source} refreshedAt={fetchedAt} />}
          {rule && <span className="text-[10px] text-slate-500" title={rule}>{t("ruleLabel")}</span>}
        </span>
      </div>

      {status === "loading" && <p className="mt-3 text-sm text-slate-400">{t("loading")}</p>}

      {status === "error" && (
        <div role="alert" className="mt-3">
          <p className="text-sm text-rose-300">{t("error")}</p>
          <p className="mt-1 text-xs text-slate-500">{t("errorHint")}</p>
        </div>
      )}

      {status === "empty" && (
        <div className="mt-3">
          <p className="text-sm text-slate-400" data-testid="watch-empty">{t("empty")}</p>
          {deadlinesStatus === "source_pending" && <p className="mt-1 text-xs text-slate-500">{t("deadlinesPending")}</p>}
        </div>
      )}

      {status === "ready" && (
        <>
          <section className="mt-3" aria-label={t("eventsTitle")}>
            <h4 className="text-xs font-bold uppercase tracking-wider text-sky-300">{t("eventsTitle")}</h4>
            {eventsStatus === "source_pending" && events.length === 0 && (
              <p className="mt-1 text-xs text-amber-200" data-testid="watch-events-pending">{t("eventsPending")}</p>
            )}
            {events.length === 0 && eventsStatus === "success" && <p className="mt-1 text-sm text-slate-400">{t("empty")}</p>}
            <ul className="mt-2 space-y-1.5">
              {events.map((e) => (
                <li key={e.event_id} data-testid={`watch-event-${e.event_id}`} className="rounded-lg border border-white/10 bg-slate-800/60 px-2 py-1.5">
                  <div className="flex flex-wrap items-center justify-between gap-2">
                    <span className="text-sm font-semibold">{e.title}</span>
                    <span className="rounded-full bg-sky-500/20 px-2 py-0.5 text-[10px] font-bold text-sky-200">
                      {e.kind === "deadline_soon" ? t("kindDeadlineSoon") : t("kindNewPermit")}
                    </span>
                  </div>
                  <div className="mt-1 flex flex-wrap items-center gap-2 text-xs text-slate-400">
                    <span>
                      {typeof e.distance_m === "number"
                        ? t("distanceM", { n: Math.round(e.distance_m) })
                        : t("distanceUnknown")}
                    </span>
                    <span>· {e.deadline}</span>
                    <SourceTrustBadge state={e.trust_state} source={e.source} refreshedAt={e.fetched_at} />
                    <a href={e.source_url} target="_blank" rel="noreferrer" className="truncate text-sky-300">
                      {t("sourceLink")}
                    </a>
                  </div>
                </li>
              ))}
            </ul>
          </section>

          <section className="mt-4" aria-label={t("deadlinesTitle")}>
            <h4 className="text-xs font-bold uppercase tracking-wider text-sky-300">{t("deadlinesTitle")}</h4>
            <ul className="mt-2 space-y-1.5">
              {deadlines.map((d) => {
                const state = effectiveState(d);
                return (
                  <li
                    key={d.baugesuch_id}
                    data-testid={`watch-deadline-${d.baugesuch_id}`}
                    data-state={state}
                    className="rounded-lg border border-white/10 bg-slate-800/60 px-2 py-2"
                  >
                    <div className="flex flex-wrap items-center justify-between gap-2">
                      <span className="text-sm font-semibold">{d.title}</span>
                      <span className={`rounded-full px-2 py-0.5 text-[10px] font-bold ${deadlineTone(state)}`}>
                        {stateLabel(state)}
                      </span>
                    </div>
                    <p className="mt-1 text-xs text-slate-400">
                      {d.municipality} · {t("publication")} {d.publication_date} · {t("deadlineLabel")} {d.deadline} ·{" "}
                      <span className={`font-semibold ${state === "expired" ? "text-rose-200" : state === "due_soon" ? "text-amber-200" : "text-sky-200"}`}>
                        <Countdown item={d} t={t} />
                      </span>
                    </p>
                    <p className="mt-1 rounded bg-amber-500/10 px-2 py-1 text-[11px] leading-4 text-amber-200/90">
                      {t("disclaimer")}
                    </p>
                    <p className="mt-1 text-[10px] text-slate-500">
                      {t("ruleLabel")}: {d.rule || rule || ""}
                    </p>
                  </li>
                );
              })}
            </ul>
          </section>

          <form
            className="mt-4 border-t border-white/10 pt-3"
            onSubmit={(e) => {
              e.preventDefault();
              onSubmit?.();
            }}
          >
            <h4 className="text-xs font-bold uppercase tracking-wider text-sky-300">{t("zoneTitle")}</h4>
            <fieldset className="mt-2 flex flex-wrap items-center gap-3">
              <legend className="sr-only">{t("channelsLabel")}</legend>
              {(["push", "email"] as WatchChannel[]).map((c) => (
                <label key={c} className="flex items-center gap-1.5 text-xs text-slate-300">
                  <input
                    type="checkbox"
                    name="watch-channel"
                    value={c}
                    checked={channels.includes(c)}
                    onChange={() => onToggleChannel?.(c)}
                  />
                  {c === "push" ? t("channelPush") : t("channelEmail")}
                </label>
              ))}
            </fieldset>
            {channels.includes("email") && (
              <label className="mt-2 block text-xs text-slate-300">
                {t("emailLabel")}
                <input
                  type="email"
                  name="watch-email"
                  value={email}
                  onChange={(e) => onEmailChange?.(e.target.value)}
                  placeholder={t("emailPlaceholder")}
                  className="ml-2 rounded border border-white/10 bg-slate-950/60 px-2 py-1 text-xs"
                />
              </label>
            )}
            {channels.includes("push") && (
              <>
                <label className="mt-2 block text-xs text-slate-300">
                  {t("pushEndpointLabel")}
                  <input
                    type="url"
                    name="watch-push-endpoint"
                    value={subscriptionEndpoint}
                    onChange={(e) => onSubscriptionEndpointChange?.(e.target.value)}
                    placeholder={t("pushEndpointPlaceholder")}
                    className="ml-2 rounded border border-white/10 bg-slate-950/60 px-2 py-1 text-xs"
                  />
                </label>
                <p className="mt-1 text-[11px] text-amber-200/80">{t("pushHint")}</p>
              </>
            )}
            <label className="mt-2 flex items-start gap-2 text-xs text-slate-300">
              <input
                type="checkbox"
                name="watch-consent"
                checked={consent}
                onChange={(e) => onConsentChange?.(e.target.checked)}
                className="mt-0.5"
              />
              <span>{t("consentLabel")}</span>
            </label>
            <p className="mt-1 text-[11px] text-slate-500">{t("channelsHint")}</p>
            <div className="mt-2 flex flex-wrap items-center gap-2">
              <button
                type="submit"
                data-testid="watch-submit"
                disabled={!!consentReason && !consentReason.ok}
                title={reasonText}
                className="rounded-lg border border-sky-500/40 bg-sky-500/20 px-3 py-1.5 text-xs font-semibold text-white disabled:opacity-50"
              >
                {t("submit")}
              </button>
              {reasonText && <span data-testid="watch-consent-reason" className="text-xs text-amber-200">{reasonText}</span>}
              {submitMessage && (
                <span
                  data-testid="watch-submit-status"
                  role={submitMessage.ok ? "status" : "alert"}
                  className={`text-xs ${submitMessage.ok ? "text-emerald-300" : "text-rose-300"}`}
                >
                  {submitMessage.text}
                </span>
              )}
            </div>
          </form>
        </>
      )}
    </article>
  );
}

/** Container: fetches the two watch endpoints with last-request-wins semantics. */
export default function WatchEventsCard({ postcode }: { postcode?: string }) {
  const t = useTranslations("resident.feature023");
  const [state, setState] = useState<{
    status: WatchFetchStatus;
    events: WatchEventItem[];
    deadlines: WatchDeadlineItem[];
    eventsStatus: SubFetchStatus;
    deadlinesStatus: SubFetchStatus;
    fetchedAt: string;
    source: string;
    trustState: WatchTrustState;
    rule: string;
  }>({
    status: "loading",
    events: [],
    deadlines: [],
    eventsStatus: "success",
    deadlinesStatus: "success",
    fetchedAt: "",
    source: "",
    trustState: "official_publication",
    rule: "",
  });
  const [consent, setConsent] = useState(false);
  const [channels, setChannels] = useState<WatchChannel[]>(["email"]);
  const [email, setEmail] = useState("");
  const [subscriptionEndpoint, setSubscriptionEndpoint] = useState("");
  const [submitMessage, setSubmitMessage] = useState<{ ok: boolean; text: string } | null>(null);
  const seq = useRef(0);

  useEffect(() => {
    if (!postcode) return;
    const my = ++seq.current;
    const controller = new AbortController();
    setState((s) => ({ ...s, status: "loading" }));
    const results = Promise.allSettled([
      fetchWatchEvents(50, controller.signal),
      fetchWatchDeadlines(postcode, controller.signal),
    ]);
    results
      .then(([ev, dl]) => {
        if (seq.current !== my) return;
        const events = ev.status === "fulfilled" ? ev.value : null;
        const deadlines = dl.status === "fulfilled" ? dl.value : null;
        const mapped = toViewData(deadlines, events, postcode);
        setState({
          ...mapped,
          source: events?.source || deadlines?.source || "",
          trustState: (events?.trust_state || deadlines?.trust_state || "official_publication") as WatchTrustState,
          rule: deadlines?.rule ?? "",
        });
      })
      .catch(() => {
        if (seq.current !== my) return;
        setState((s) => ({ ...s, status: "error", events: [], deadlines: [] }));
      });
    return () => controller.abort();
  }, [postcode]);

  const consentReason = useMemo<ZoneBuildResult | null>(() => {
    if (!postcode) return null;
    const built = buildZoneRequest({ postcode, channels, consent, email, subscriptionEndpoint });
    return built.ok ? null : built;
  }, [postcode, channels, consent, email, subscriptionEndpoint]);

  const onSubmit = useCallback(() => {
    if (!postcode) return;
    const built = buildZoneRequest({ postcode, channels, consent, email, subscriptionEndpoint });
    if (!built.ok) {
      setSubmitMessage({ ok: false, text: t(built.error) });
      return;
    }
    createWatchZone(built.request)
      .then(() => setSubmitMessage({ ok: true, text: t("submitOk") }))
      .catch(() => setSubmitMessage({ ok: false, text: t("submitError") }));
  }, [postcode, channels, consent, email, subscriptionEndpoint, t]);

  if (!postcode) return null;

  return (
    <WatchEventsView
      {...state}
      postcode={postcode}
      consent={consent}
      channels={channels}
      email={email}
      subscriptionEndpoint={subscriptionEndpoint}
      consentReason={consentReason}
      submitMessage={submitMessage}
      onToggleChannel={(c) => setChannels((prev) => (prev.includes(c) ? prev.filter((x) => x !== c) : [...prev, c]))}
      onConsentChange={setConsent}
      onEmailChange={setEmail}
      onSubscriptionEndpointChange={setSubscriptionEndpoint}
      onSubmit={onSubmit}
    />
  );
}
