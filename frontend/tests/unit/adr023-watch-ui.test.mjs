/**
 * ADR-023/B component tests: WatchEventsCard (watch events + Einsprachefrist UI).
 *
 * Traceability (ADR-023 / SPEC-060):
 * - REQ-A3  -> events carry source/fetched_at/trust_state -> SourceTrustBadge rendered.
 * - REQ-B1  -> deadline comes from the backend (publication_date + documented rule).
 * - REQ-B2  -> expired is never rendered as open; due_soon threshold is 3 days.
 * - REQ-B3  -> disclaimer is rendered next to the countdown.
 * - REQ-A1  -> zone is only submitted with consent + at least one channel.
 * - SPEC-060 REQ-060-003 -> loading / ready / empty / error states.
 *
 * Harness: the real component (.tsx) is compiled in-process with sucrase and
 * rendered with react-dom/server through the real next-intl provider, so the
 * assertions below run against production markup, not a copy of it.
 */

import { test } from "node:test";
import assert from "node:assert/strict";
import fs from "node:fs";
import path from "node:path";
import { createRequire } from "node:module";
import { fileURLToPath } from "node:url";

const require = createRequire(import.meta.url);
const HERE = path.dirname(fileURLToPath(import.meta.url));
const FRONTEND = path.resolve(HERE, "..", "..");
const SRC = path.join(FRONTEND, "src");
const LOCALES = ["de", "en", "fr", "it"];

// --- in-process TSX harness --------------------------------------------------
const { transform } = require("sucrase");
for (const ext of [".tsx", ".ts"]) {
  require.extensions[ext] = function compile(mod, filename) {
    const code = transform(fs.readFileSync(filename, "utf8"), {
      transforms: ["typescript", "jsx", "imports"],
      jsxRuntime: "automatic",
      filePath: filename,
    }).code;
    mod._compile(code, filename);
  };
}
const Module = require("node:module");
const nativeResolve = Module._resolveFilename;
Module._resolveFilename = function resolveAlias(request, ...rest) {
  if (request.startsWith("@/")) {
    return nativeResolve.call(this, path.join(SRC, request.slice(2)), ...rest);
  }
  return nativeResolve.call(this, request, ...rest);
};

const React = require("react");
const { renderToStaticMarkup } = require("react-dom/server");
const { NextIntlClientProvider } = require("next-intl");

const messages = Object.fromEntries(
  LOCALES.map((l) => [l, JSON.parse(fs.readFileSync(path.join(FRONTEND, "messages", `${l}.json`), "utf8"))])
);

const CARD = require(path.join(SRC, "components", "WatchEventsCard.tsx"));

function msg(locale, key) {
  return messages[locale].resident.feature023[key];
}

function render(locale, element) {
  return renderToStaticMarkup(
    React.createElement(
      NextIntlClientProvider,
      { locale, messages: messages[locale], timeZone: "Europe/Zurich" },
      element
    )
  );
}

function viewHtml(locale, props) {
  return render(locale, React.createElement(CARD.WatchEventsView, props));
}

// --- realistic backend payloads (ADR-023/A contract) -------------------------
const STAMP = "2026-09-24T09:00:00+00:00";

function deadlineItem(over) {
  return {
    baugesuch_id: "zh-8004-77",
    zone_id: "zone-8004",
    postcode: "8004",
    municipality: "Zürich",
    title: "Neubau Mehrfamilienhaus",
    publication_date: "2026-09-10",
    deadline: "2026-09-30",
    days_left: 6,
    state: "open",
    source_url: "https://amtsblattportal.ch/de/publications/77",
    source: "Kantonale E-Amtsblätter",
    trust_state: "official_publication",
    disclaimer: "Keine Rechtsberatung; ersetzt weder anwaltliche Beratung noch Vertretung.",
    rule: "deadline = publication_date + 20 Tage (Standardfrist, ADR-023)",
    ...over,
  };
}

function eventItem(over) {
  return {
    event_id: "zone-8004:zh-8004-77:new_permit",
    zone_id: "zone-8004",
    baugesuch_id: "zh-8004-77",
    kind: "new_permit",
    distance_m: 412.7,
    title: "Neubau Mehrfamilienhaus",
    postcode: "8004",
    canton: "ZH",
    publication_date: "2026-09-10",
    deadline: "2026-09-30",
    days_left: 6,
    state: "open",
    source_url: "https://amtsblattportal.ch/de/publications/77",
    source: "Kantonale E-Amtsblätter",
    trust_state: "official_publication",
    fetched_at: STAMP,
    delivery: [{ channel: "email", status: "queued_pending_opt_in", detail: "confirmation_pending" }],
    ...over,
  };
}

function viewProps(over = {}) {
  return {
    status: "ready",
    events: [eventItem()],
    deadlines: [deadlineItem()],
    eventsStatus: "success",
    deadlinesStatus: "success",
    postcode: "8004",
    fetchedAt: STAMP,
    source: "Kantonale E-Amtsblätter",
    disclaimer: undefined,
    rule: undefined,
    onSubmit: () => {},
    ...over,
  };
}

// --- REQ-060-003: honest empty state ----------------------------------------
test("adr023b: empty state honestly says there is no new event", () => {
  for (const locale of LOCALES) {
    const html = viewHtml(locale, viewProps({ status: "empty", events: [], deadlines: [] }));
    assert.ok(
      html.includes(msg(locale, "empty")),
      `[${locale}] expected honest empty message in markup: ${html.slice(0, 400)}`
    );
    assert.ok(!html.includes("data-testid=\"watch-deadline-"), `[${locale}] empty state must not render deadline rows`);
    assert.ok(!html.includes("data-testid=\"watch-event-"), `[${locale}] empty state must not render event rows`);
    // no invented state/kind markup without a real deadline or event
    assert.ok(!html.includes("data-state="), `[${locale}] no deadline state may be invented`);
    assert.ok(
      !html.includes(msg(locale, "kindNewPermit")) && !html.includes(msg(locale, "kindDeadlineSoon")),
      `[${locale}] no event kind may be invented`
    );
  }
});

// --- REQ-B2: expired is never rendered as open ------------------------------
test("adr023b: expired deadline is never rendered as open", () => {
  for (const locale of LOCALES) {
    const expired = deadlineItem({ baugesuch_id: "zh-expired", days_left: -4, state: "expired", deadline: "2026-09-20" });
    const html = viewHtml(locale, viewProps({ deadlines: [expired] }));
    assert.ok(html.includes('data-state="expired"'), `[${locale}] expired row must carry data-state=expired`);
    assert.ok(
      html.includes(msg(locale, "stateExpired")),
      `[${locale}] expired row must use the expired label`
    );
    assert.ok(
      !new RegExp(`data-state="expired"[^>]*>[^<]*${msg(locale, "stateOpen")}`).test(html),
      `[${locale}] expired row must not be labelled open`
    );
    assert.ok(
      !html.includes(msg(locale, "stateOpen")),
      `[${locale}] no open label may appear when the only deadline is expired`
    );
    // the tone must differ from the open tone so colour alone is not the signal either
    assert.notEqual(
      CARD.deadlineTone("expired"),
      CARD.deadlineTone("open"),
      "expired and open must not share the same tone"
    );
    assert.ok(html.includes(CARD.deadlineTone("expired").split(" ")[0]), `[${locale}] expired tone class missing`);
  }
});

// --- REQ-B2: due_soon threshold is 3 days -----------------------------------
test("adr023b: countdown follows the 3-day due_soon threshold", () => {
  const cases = [
    { days_left: 3, state: "due_soon", label: "stateDueSoon" },
    { days_left: 1, state: "due_soon", label: "stateDueSoon" },
    { days_left: 4, state: "open", label: "stateOpen" },
    { days_left: 0, state: "due_soon", label: "stateDueSoon" },
  ];
  for (const c of cases) {
    const html = viewHtml("de", viewProps({ deadlines: [deadlineItem(c)] }));
    assert.ok(html.includes(`data-state="${c.state}"`), `days_left=${c.days_left} -> data-state=${c.state}`);
    assert.ok(html.includes(msg("de", c.label)), `days_left=${c.days_left} -> label ${c.label}`);
    assert.ok(
      html.includes(msg("de", c.days_left === 0 ? "dueToday" : "daysLeft").replace("{n}", String(c.days_left))),
      `days_left=${c.days_left} -> localized countdown text`
    );
  }
  const past = viewHtml("de", viewProps({ deadlines: [deadlineItem({ days_left: -5, state: "expired" })] }));
  assert.ok(
    past.includes(msg("de", "expiredAgo").replace("{n}", "5")),
    "an expired deadline states how long it has been expired"
  );
});

// --- REQ-A3: events carry distance/kind/source/trust -------------------------
test("adr023b: event rows show distance, kind and source trust", () => {
  const html = viewHtml("de", viewProps());
  assert.ok(html.includes('data-testid="watch-event-zone-8004:zh-8004-77:new_permit"'), "event row testid");
  assert.ok(html.includes("413"), "distance is rendered in metres (rounded from 412.7)");
  assert.ok(html.includes(msg("de", "kindNewPermit")), "event kind label");
  assert.ok(html.includes("official publication"), "SourceTrustBadge renders the backend trust_state");
  assert.ok(html.includes("Kantonale E-Amtsblätter"), "event source name is visible");
  assert.ok(html.includes("2026-09-24T09:00:00+00:00"), "fetched_at is passed to the trust badge title");

  const soon = viewHtml("de", viewProps({ events: [eventItem({ kind: "deadline_soon" })] }));
  assert.ok(soon.includes(msg("de", "kindDeadlineSoon")), "deadline_soon kind label");

  const unknown = viewHtml("de", viewProps({ events: [eventItem({ distance_m: null })] }));
  assert.ok(unknown.includes(msg("de", "distanceUnknown")), "unknown distance stays explicit, never 0 m");
});

// --- REQ-B3: disclaimer sits next to the countdown --------------------------
test("adr023b: REQ-B3 disclaimer is rendered next to the countdown", () => {
  const html = viewHtml("de", viewProps());
  const rowStart = html.indexOf('data-testid="watch-deadline-zh-8004-77"');
  const rowEnd = html.indexOf("</li>", rowStart);
  assert.ok(rowStart >= 0 && rowEnd > rowStart, "deadline row rendered");
  const row = html.slice(rowStart, rowEnd);
  // the warning is always the localized one (never raw backend German in
  // en/fr/it), sitting inside the same row as the countdown
  assert.ok(row.includes(msg("de", "disclaimer")), "localized disclaimer inside the deadline row");
  assert.ok(row.includes(msg("de", "daysLeft").replace("{n}", "6")), "countdown inside the same row");
  for (const locale of LOCALES) {
    const localized = viewHtml(locale, viewProps());
    const start = localized.indexOf('data-testid="watch-deadline-zh-8004-77"');
    const end = localized.indexOf("</li>", start);
    const lrow = localized.slice(start, end);
    assert.ok(lrow.includes(msg(locale, "disclaimer")), `[${locale}] localized disclaimer inside the row`);
    if (locale !== "de") {
      assert.ok(!lrow.includes(msg("de", "disclaimer")), `[${locale}] no raw German disclaimer string`);
    }
  }
  const customRule = viewHtml("de", viewProps({ deadlines: [deadlineItem()], rule: "deadline = publication_date + 30 Tage (Kanton X)" }));
  assert.ok(customRule.includes("30 Tage"), "backend-provided rule text wins over the default");
});

// --- REQ-A1: consent gate ----------------------------------------------------
test("adr023b: no zone is submitted without consent and a channel", () => {
  const base = { postcode: "8004", channels: ["email"], email: "resident@example.ch", consent: true };
  const ok = CARD.buildZoneRequest(base);
  assert.equal(ok.ok, true, "consent + email channel is submittable");
  assert.deepEqual(ok.request.channels, ["email"]);
  assert.equal(ok.request.consent, true);
  assert.equal(ok.request.zone_id, "zone-8004");
  assert.equal(ok.request.postcode, "8004");
  assert.equal(ok.request.radius_m, 500);
  assert.ok(ok.request.lat >= 45 && ok.request.lat <= 48, "pilot postcode centre latitude sent to the API");

  assert.deepEqual(CARD.buildZoneRequest({ ...base, consent: false }), { ok: false, error: "consentRequired" });
  assert.deepEqual(CARD.buildZoneRequest({ ...base, channels: [] }), { ok: false, error: "noChannel" });
  assert.deepEqual(CARD.buildZoneRequest({ ...base, email: "" }), { ok: false, error: "emailRequired" });
  const push = CARD.buildZoneRequest({ postcode: "8004", channels: ["push"], consent: true });
  assert.deepEqual(push, { ok: false, error: "pushRequired" }, "push without a real subscription endpoint is refused");
  const pushOk = CARD.buildZoneRequest({
    postcode: "8004",
    channels: ["push"],
    consent: true,
    subscriptionEndpoint: "https://push.example/abc",
  });
  assert.equal(pushOk.ok, true);
  assert.equal(pushOk.request.subscription_endpoint, "https://push.example/abc");
});

test("adr023b: channel selector and consent control are rendered with a reason when blocked", () => {
  const html = viewHtml("de", viewProps());
  assert.ok(html.includes(msg("de", "channelPush")), "push channel option");
  assert.ok(html.includes(msg("de", "channelEmail")), "email channel option");
  assert.ok(html.includes('type="checkbox"'), "consent is an explicit checkbox");
  assert.ok(html.includes(msg("de", "consentLabel")), "consent label explains the opt-in");
  assert.ok(html.includes("watch-consent-reason") || html.includes(msg("de", "channelsHint")), "blocked submit reason is programmatically available");
});

// --- SPEC-060 REQ-060-003: states -------------------------------------------
test("adr023b: loading, error and source-pending states are explicit", () => {
  const loading = viewHtml("de", viewProps({ status: "loading", events: [], deadlines: [] }));
  assert.ok(loading.includes(msg("de", "loading")), "loading state");
  assert.ok(loading.includes('aria-live="polite"'), "loading is announced");

  const error = viewHtml("de", viewProps({ status: "error", events: [], deadlines: [] }));
  assert.ok(error.includes(msg("de", "error")), "error state");
  assert.ok(error.includes(msg("de", "errorHint")), "error hint");
  assert.ok(error.includes('role="alert"'), "error is an alert");
  assert.ok(!error.includes("data-testid=\"watch-event-"), "no invented events on error");

  const partial = viewHtml("de", viewProps({ eventsStatus: "source_pending", events: [], deadlines: [deadlineItem()] }));
  assert.ok(partial.includes(msg("de", "eventsPending")), "failed sub-fetch is disclosed, deadlines still shown");
  assert.ok(partial.includes('data-testid="watch-deadline-zh-8004-77"'), "deadlines survive an events outage");
});

// --- i18n: resident.feature023 in de/en/fr/it, no hardcoded German -----------
test("adr023b: all four locales expose the same resident.feature023 keys", () => {
  const base = Object.keys(messages.de.resident.feature023).sort();
  for (const locale of LOCALES) {
    const keys = Object.keys(messages[locale].resident.feature023 ?? {}).sort();
    assert.deepEqual(keys, base, `[${locale}] resident.feature023 key set must match de`);
    for (const key of keys) {
      assert.ok(String(msg(locale, key)).trim().length > 0, `[${locale}] empty value for ${key}`);
    }
  }
});

test("adr023b: no hardcoded German leaks into en/fr/it", () => {
  // Keys that a ready view always renders (placeholders already substituted).
  const alwaysRendered = [
    "title", "disclaimer", "submit", "channelEmail", "channelPush", "consentLabel", "stateOpen",
    "eventsTitle", "deadlinesTitle", "zoneTitle", "channelsLabel", "emailLabel",
    "publication", "deadlineLabel", "ruleLabel", "sourceLink",
  ];
  const withValues = { daysLeft: 6, distanceM: 413 };
  for (const locale of ["en", "fr", "it"]) {
    const ready = viewHtml(locale, viewProps());
    const empty = viewHtml(locale, viewProps({ status: "empty", events: [], deadlines: [] }));
    for (const key of alwaysRendered) {
      assert.ok(ready.includes(msg(locale, key)), `[${locale}] ready view must render ${key}=${msg(locale, key)}`);
    }
    for (const [key, n] of Object.entries(withValues)) {
      const expected = msg(locale, key).replace("{n}", String(n));
      assert.ok(ready.includes(expected), `[${locale}] ready view must render ${expected}`);
      assert.ok(!ready.includes(msg("de", key).replace("{n}", String(n))), `[${locale}] no German ${key}`);
    }
    assert.ok(empty.includes(msg(locale, "empty")), `[${locale}] empty view must render the localized empty message`);
    for (const key of Object.keys(messages.de.resident.feature023)) {
      const german = msg("de", key);
      if (german === msg(locale, key) || german.includes("{")) continue;
      assert.ok(!ready.includes(german), `[${locale}] ready view must not contain the German ${key}="${german}"`);
      assert.ok(!empty.includes(german), `[${locale}] empty view must not contain the German ${key}="${german}"`);
    }
  }
});

// --- view-model mapping ------------------------------------------------------
test("adr023b: view model keeps only events of the active place and stays honest when empty", () => {
  const foreign = eventItem({ event_id: "zone-3011:zh-3011-1:new_permit", postcode: "3011" });
  const events = {
    status: "success",
    count: 2,
    items: [eventItem(), foreign],
    source: "Kantonale E-Amtsblätter",
    trust_state: "official_publication",
    fetched_at: STAMP,
  };
  const noDeadlines = {
    status: "success",
    count: 0,
    items: [],
    rule: "deadline = publication_date + 20 Tage (Standardfrist, ADR-023)",
    disclaimer: "Keine Rechtsberatung.",
    source: "Kantonale E-Amtsblätter",
    trust_state: "source_pending",
    fetched_at: STAMP,
  };

  const mapped = CARD.toViewData(noDeadlines, events, "8004");
  assert.equal(mapped.events.length, 1, "only events of the searched postcode are shown");
  assert.equal(mapped.events[0].postcode, "8004");
  assert.equal(mapped.status, "ready", "a matching event keeps the card in ready");

  const onlyForeign = CARD.toViewData(noDeadlines, { ...events, items: [foreign] }, "8004");
  assert.equal(onlyForeign.events.length, 0, "a foreign postcode is never shown as our event");
  assert.equal(onlyForeign.status, "empty", "no matched deadline and no matched event -> honest empty");

  const deadlinesOnly = CARD.toViewData(
    { ...noDeadlines, count: 1, status: "success", items: [deadlineItem()] },
    { ...events, status: "source_pending", items: [] },
    "8004"
  );
  assert.equal(deadlinesOnly.status, "ready", "deadlines alone still populate the card");
  assert.equal(deadlinesOnly.eventsStatus, "source_pending", "an events outage is disclosed, not hidden");
  assert.equal(deadlinesOnly.deadlinesStatus, "success");

  const totalFailure = CARD.toViewData(null, null, "8004");
  assert.equal(totalFailure.status, "error", "both sub-fetches failing is an explicit error");
  assert.equal(totalFailure.eventsStatus, "error");
  assert.equal(totalFailure.deadlinesStatus, "error");
});
