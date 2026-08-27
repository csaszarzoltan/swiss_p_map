"use client";
import { useEffect } from "react";
import type { Topic } from "@/components/TopicSidebar";

export type Shared = {
  plz?: string;
  topic: Topic;
  selected?: string | null;
  radius: number;
};

const topics = new Set(["overview", "politik", "ort", "planung", "solar", "oereb"]);

export function parseShareableState(s: string): Partial<Shared> {
  const p = new URLSearchParams(s);
  const plz = p.get("plz");
  const topic = p.get("topic");
  const radius = Number(p.get("radius"));
  return {
    ...(plz && /^\d{4}$/.test(plz) ? { plz } : {}),
    ...(topic && topics.has(topic) ? { topic: topic as Topic } : {}),
    ...(p.get("selected") ? { selected: p.get("selected") } : {}),
    ...([300, 500, 1000].includes(radius) ? { radius } : {}),
  };
}

export function useShareableState(state: Shared, restore: (s: Partial<Shared>) => void): void {
  // Restore once on mount
  useEffect(() => {
    restore(parseShareableState(typeof window !== "undefined" ? window.location.search : ""));
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  // Sync state → URL, but preserve existing ?plz= if state.plz not yet set (deep-link restore race)
  useEffect(() => {
    if (typeof window === "undefined") return;
    const current = new URLSearchParams(window.location.search);
    const p = new URLSearchParams(current.toString());
    // plz: only overwrite when state has it; otherwise keep current URL's plz
    if (state.plz) p.set("plz", state.plz);
    else if (!state.plz && !current.get("plz")) p.delete("plz");
    // topic
    if (state.topic !== "overview") p.set("topic", state.topic);
    else p.delete("topic");
    // selected
    if (state.selected) p.set("selected", state.selected);
    else p.delete("selected");
    // radius
    if (state.radius !== 500) p.set("radius", String(state.radius));
    else p.delete("radius");
    const qs = p.toString();
    const next = window.location.pathname + (qs ? `?${qs}` : "");
    if (next !== window.location.pathname + window.location.search) {
      history.replaceState(null, "", next);
    }
  }, [state]);

  return;
}
