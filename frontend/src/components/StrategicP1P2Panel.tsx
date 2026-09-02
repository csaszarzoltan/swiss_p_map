"use client";

type Data = Record<string, unknown>;
export default function StrategicP1P2Panel({ data, topic }: { data?: Record<string, Data>; topic: string }) {
  if (!data || !["overview", "ort", "solar"].includes(topic)) return null;
  const cards = [
    ["microclimate", "Mikroklima · CH2025", "Sommerliche Wärmeinsel und Tropennächte"],
    ["education", "Bildung", "Kindergarten, Primarschule und Sekundarstufe II"],
    ["energy", "Gebäudeenergie", "Heizung, Fernwärme, Geothermie und Fördercheck"],
    ["airPollen", "Luft & Pollen", "NABEL PM10/PM2.5/NO₂/Ozon und Pollen"],
    ["healthcare", "Gesundheit", "Apotheke, Notfallpraxis und Spital"],
    ["connectivity", "Digitale Infrastruktur", "FTTH, 5G und Download-Bandbreite"],
  ] as const;
  return <section data-testid="strategic-p1-p2-panel" className="mb-5 grid gap-3 md:grid-cols-2 xl:grid-cols-3">
    {cards.map(([key,title,subtitle]) => data[key] ? <article key={key} data-testid={`${key}-card`} className="rounded-xl border border-cyan-500/25 bg-slate-900/70 p-4">
      <h3 className="text-xs font-bold uppercase tracking-wider text-cyan-300">{title}</h3><p className="mt-1 text-sm text-slate-300">{subtitle}</p>
      <pre className="mt-2 max-h-36 overflow-auto whitespace-pre-wrap text-[10px] text-slate-400">{JSON.stringify(data[key], null, 2)}</pre>
    </article> : null)}
  </section>;
}
