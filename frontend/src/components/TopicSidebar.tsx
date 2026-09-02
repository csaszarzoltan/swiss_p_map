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
    <nav data-testid="topic-sidebar" className="flex items-center gap-2 overflow-x-auto no-scrollbar px-3 py-2.5 sm:px-4 sm:py-3">
      {TOPICS.map(({ id, icon, labelKey }) => {
        const active = activeTopic === id;
        const count = counts[id] ?? 0;
        return (
          <button
            key={id}
            data-testid={`menu-${id}`}
            onClick={() => onSelect(id)}
            className={`group relative flex items-center gap-2 shrink-0 rounded-full px-4 py-2 text-xs sm:text-sm font-semibold tracking-wide transition-all duration-200 ${
              active
                ? "bg-gradient-to-r from-sky-500 to-blue-600 text-white shadow-lg shadow-sky-500/25 ring-1 ring-white/30"
                : "glass-pill text-slate-300 hover:text-white hover:bg-slate-800/80 hover:border-white/20"
            }`}
          >
            <span className="text-sm sm:text-base leading-none transition-transform group-hover:scale-110">{icon}</span>
            <span>{t(labelKey)}</span>
            {count > 0 && (
              <span
                data-testid={`menu-count-${id}`}
                className={`rounded-full px-2 py-0.5 text-[10px] sm:text-[11px] font-bold leading-none transition-colors ${
                  active ? "bg-white/25 text-white" : "bg-sky-500/20 text-sky-300 border border-sky-500/30"
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
