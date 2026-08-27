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
    <nav data-testid="topic-sidebar" className="flex flex-wrap gap-1.5 border-y border-white/10 bg-[#0b1220] px-4 py-3">
      {TOPICS.map(({ id, icon, labelKey }) => {
        const active = activeTopic === id;
        const count = counts[id] ?? 0;
        return (
          <button
            key={id}
            data-testid={`menu-${id}`}
            onClick={() => onSelect(id)}
            className={`flex items-center gap-2 rounded-full px-4 py-2 text-sm font-medium transition ${
              active
                ? "bg-white text-slate-900 shadow"
                : "border border-white/10 bg-white/[0.06] text-slate-200 hover:bg-white/15 hover:text-white"
            }`}
          >
            <span className="text-base leading-none">{icon}</span>
            <span>{t(labelKey)}</span>
            {count > 0 && (
              <span
                data-testid={`menu-count-${id}`}
                className={`rounded-full px-1.5 py-0.5 text-[11px] font-bold leading-none ${
                  active ? "bg-slate-900 text-white" : "bg-sky-500/20 text-sky-200"
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
