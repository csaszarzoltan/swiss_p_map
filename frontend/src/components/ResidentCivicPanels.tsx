"use client";

import { useEffect, useState } from "react";

type CivicData = Record<string, unknown>;

export default function ResidentCivicPanels({ postcode }: { postcode: string }) {
  const [active, setActive] = useState("votes");
  const [data, setData] = useState<Record<string, CivicData>>({});
  const base = process.env.NEXT_PUBLIC_API_URL ?? "http://127.0.0.1:8310";
  useEffect(() => {
    const routes: Record<string, string> = {
      votes: "/api/v1/votes/proposals",
      news: `/api/v1/news/local?postcode=${postcode}`,
      weather: `/api/v1/weather/current?postcode=${postcode}`,
      municipal: `/api/v1/municipal/waste-calendar?postcode=${postcode}`,
    };
    const controller = new AbortController();
    Promise.all(Object.entries(routes).map(async ([key, path]) => {
      const response = await fetch(`${base}${path}`, { signal: controller.signal });
      return [key, response.ok ? await response.json() as CivicData : { status: "error" }] as const;
    })).then((items) => setData(Object.fromEntries(items))).catch(() => undefined);
    return () => controller.abort();
  }, [base, postcode]);
  const tabs = ["votes", "news", "weather", "municipal"];
  return <section className="mt-4 rounded-2xl border border-white/10 bg-slate-950/40 p-4">
    <div role="tablist" aria-label="Civic intelligence">{tabs.map((tab) => <button key={tab} role="tab" aria-selected={active === tab} onClick={() => setActive(tab)} className="m-1 rounded-lg border border-white/10 px-3 py-2">{tab}</button>)}</div>
    <div role="tabpanel" aria-live="polite" className="mt-3"><pre className="max-h-64 overflow-auto whitespace-pre-wrap text-xs text-slate-300">{JSON.stringify(data[active] ?? { status: "loading" }, null, 2)}</pre></div>
  </section>;
}
