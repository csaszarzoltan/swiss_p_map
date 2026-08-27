"use client";

import { useTranslations } from "next-intl";

export type Topic = "overview" | "politik" | "ort" | "planung" | "solar" | "oereb";

export interface TopicSidebarProps {
  activeTopic: Topic;
  onSelect: (t: Topic) => void;
  counts: Record<Topic, number>;
}

const TOPICS: { id: Topic; icon: string; labelKey: string }[] = [
  { id: "overview", icon: "◉", labelKey: "menu.overview" },
  { id: "politik", icon: "🏛", labelKey: "menu.politik" },
  { id: "ort", icon: "📍", labelKey: "menu.ort" },
  { id: "planung", icon: "🏗", labelKey: "menu.planung" },
  { id: "solar", icon: "☀", labelKey: "menu.solar" },
  { id: "oereb", icon: "⚖", labelKey: "menu.oereb" },
];

export default function TopicSidebar({ activeTopic, onSelect, counts }: TopicSidebarProps) {
  const t = useTranslations();
  return (
    <nav data-testid="topic-sidebar" className="flex w-[200px] shrink-0 flex-col gap-1 border-r border-white/10 bg-[#0b1220] p-3">
      <p className="mb-2 px-2 text-[10px] font-semibold tracking-[0.18em] text-slate-500">THEMEN</p>
      {TOPICS.map(({ id, icon, labelKey }) => {
        const active = activeTopic === id;
        const count = counts[id] ?? 0;
        return (
          <button
            key={id}
            data-testid={`menu-${id}`}
            onClick={() => onSelect(id)}
            className={`flex items-center justify-between rounded-lg px-3 py-2.5 text-left text-sm transition ${
              active
                ? "bg-white text-slate-900 shadow"
                : "text-slate-300 hover:bg-white/10 hover:text-white"
            }`}
          >
            <span className="flex items-center gap-2.5">
              <span className="text-base leading-none">{icon}</span>
              <span className="font-medium">{t(labelKey)}</span>
            </span>
            {count > 0 && (
              <span
                data-testid={`menu-count-${id}`}
                className={`rounded-full px-1.5 py-0.5 text-[11px] font-bold leading-none ${
                  active ? "bg-slate-900 text-white" : "bg-white/15 text-slate-200"
                }`}
              >
                {count}
              </span>
            )}
          </button>
        );
      })}
    </nav>
  );
}
