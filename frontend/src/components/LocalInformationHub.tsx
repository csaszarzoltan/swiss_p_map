"use client";

import { useEffect, useState } from "react";
import ResidentCivicPanels from "./ResidentCivicPanels";

type Item = {id:string;category:string;title:string;summary:string;importance:"normal"|"important"|"urgent";status:"current_data"|"source_pending";source:string;source_url:string;map_layer?:string|null};
type Hub = {postcode:string;locality:string;generated_at:string;items:Item[];editorial_note:string};
const icons:Record<string,string>={democracy:"🗳",environment:"🌿",weather:"☁",housing:"⌂",mobility:"↔",planning:"▦"};

export default function LocalInformationHub({postcode,onOpenMap}:{postcode?:string;onOpenMap?:(layer:string)=>void}){
  const [hub,setHub]=useState<Hub|null>(null);
  useEffect(()=>{if(!postcode){setHub(null);return}const base=process.env.NEXT_PUBLIC_API_URL??"http://127.0.0.1:8310";const controller=new AbortController();fetch(`${base}/api/v1/local/briefing?postcode=${postcode}`,{signal:controller.signal}).then(r=>r.ok?r.json():Promise.reject()).then(setHub).catch(()=>setHub(null));return()=>controller.abort()},[postcode]);
  if(!postcode)return <section data-testid="local-information-hub" className="rounded-2xl border border-white/10 bg-slate-900/60 p-6"><p className="text-xs font-bold uppercase tracking-[.2em] text-sky-300">Ihr Ort. Verständlich erklärt.</p><h2 className="mt-2 text-2xl font-bold">Was heute in Ihrer Gemeinde wichtig ist</h2><p className="mt-2 max-w-3xl text-slate-400">Suchen Sie eine Postleitzahl. Danach sehen Sie Abstimmungen, Umwelt, Wetter, Wohnen, Mobilität und Bauvorhaben als getrennte Themen. Die Karte öffnet sich nur dort, wo räumlicher Kontext hilft.</p></section>;
  if(!hub)return <section aria-live="polite" className="rounded-2xl border border-white/10 p-6">Lokale Übersicht wird geladen…</section>;
  return <section data-testid="local-information-hub" aria-labelledby="local-hub-title" className="space-y-4">
    <header className="flex flex-wrap items-end justify-between gap-3"><div><p className="text-xs font-bold uppercase tracking-[.18em] text-sky-300">Lokales Briefing · {hub.postcode}</p><h2 id="local-hub-title" className="mt-1 text-2xl font-bold">Heute wichtig in {hub.locality}</h2></div><span className="text-xs text-slate-500">Quellengeprüfte Daten · Nachrichtenadapter vorbereitet</span></header>
    <div className="grid gap-3 md:grid-cols-2 xl:grid-cols-3">{hub.items.map(item=><article key={item.id} className="flex min-h-52 flex-col rounded-2xl border border-white/10 bg-slate-900/70 p-4 shadow-lg shadow-black/10">
      <div className="flex items-start justify-between gap-3"><span className="text-2xl" aria-hidden>{icons[item.category]}</span><span className={`rounded-full px-2 py-1 text-[10px] font-bold ${item.importance==="urgent"?"bg-rose-500/20 text-rose-200":item.importance==="important"?"bg-amber-500/20 text-amber-200":"bg-slate-700 text-slate-300"}`}>{item.importance}</span></div>
      <h3 className="mt-3 text-base font-bold">{item.title}</h3><p className="mt-2 flex-1 text-sm leading-6 text-slate-400">{item.summary}</p>
      <div className="mt-4 flex items-center justify-between gap-2 border-t border-white/5 pt-3"><a href={item.source_url} target="_blank" rel="noreferrer" className="truncate text-xs text-sky-300">Quelle: {item.source}</a>{item.map_layer&&<button onClick={()=>onOpenMap?.(item.map_layer!)} className="shrink-0 rounded-lg border border-white/10 px-2 py-1 text-xs hover:bg-white/10">Auf Karte</button>}</div>
    </article>)}</div>
    <ResidentCivicPanels postcode={hub.postcode} />
    <p className="rounded-xl border border-sky-500/20 bg-sky-500/5 p-3 text-xs leading-5 text-slate-400">{hub.editorial_note}</p>
  </section>
}
