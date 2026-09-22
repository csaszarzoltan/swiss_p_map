"use client";

import { useEffect, useRef, useState } from "react";
import { useTranslations } from "next-intl";
import ResidentCivicPanels from "./ResidentCivicPanels";
import SourceTrustBadge from "./SourceTrustBadge";

type Item = {id:string;category:string;title:string;summary:string;importance:"normal"|"important"|"urgent";status:"current_data"|"source_pending";source:string;source_url:string;map_layer?:string|null};
type Hub = {postcode:string;locality:string;generated_at:string;items:Item[];editorial_note:string};
type Status = "loading" | "ready" | "empty" | "error";
const icons:Record<string,string>={democracy:"🗳",environment:"🌿",weather:"☁",housing:"⌂",mobility:"↔",planning:"▦"};

const API = process.env.NEXT_PUBLIC_API_URL ?? "http://127.0.0.1:8310";

// Backend hub items are editorial composites from official sources, not live
// measurements: current_data maps to the official_publication trust badge.
function trustOf(item: Item): "official_publication" | "source_pending" {
  return item.status === "source_pending" ? "source_pending" : "official_publication";
}

export default function LocalInformationHub({postcode,onOpenMap}:{postcode?:string;onOpenMap?:(layer:string)=>void}){
  const t = useTranslations("resident.feature045");
  const [hub,setHub]=useState<Hub|null>(null);
  const [status,setStatus]=useState<Status>("loading");
  const [active,setActive]=useState(0);
  const [detail,setDetail]=useState<Item|null>(null);
  const seq=useRef(0);
  const tabRefs=useRef<Array<HTMLButtonElement|null>>([]);
  const closeBtnRef=useRef<HTMLButtonElement|null>(null);
  const lastFocus=useRef<HTMLElement|null>(null);

  // Last-request-wins: only the latest postcode fetch may update the view.
  useEffect(()=>{
    if(!postcode){setHub(null);setStatus("loading");return}
    const my=++seq.current;
    const controller=new AbortController();
    setStatus("loading");
    fetch(`${API}/api/v1/local/briefing?postcode=${encodeURIComponent(postcode)}`,{signal:controller.signal})
      .then(r=>r.ok?r.json():Promise.reject(new Error(String(r.status))))
      .then((body:Hub)=>{
        if(seq.current!==my)return;
        setHub(body);
        setActive(0);
        setStatus(!body.items||body.items.length===0?"empty":"ready");
      })
      .catch((e:unknown)=>{
        if(e instanceof DOMException&&e.name==="AbortError")return;
        if(seq.current!==my)return;
        setHub(null);
        setStatus("error");
      });
    return()=>controller.abort();
  },[postcode]);

  // Escape closes the detail modal and restores focus.
  useEffect(()=>{
    if(!detail)return;
    closeBtnRef.current?.focus();
    function onKey(e:KeyboardEvent){if(e.key==="Escape")setDetail(null)}
    document.addEventListener("keydown",onKey);
    return()=>{
      document.removeEventListener("keydown",onKey);
      lastFocus.current?.focus();
    };
  },[detail]);

  function onTabKey(e:React.KeyboardEvent,idx:number){
    const n=hub?.items.length??0;
    if(n===0)return;
    let next:number|null=null;
    if(e.key==="ArrowRight"||e.key==="ArrowDown")next=(idx+1)%n;
    else if(e.key==="ArrowLeft"||e.key==="ArrowUp")next=(idx-1+n)%n;
    else if(e.key==="Home")next=0;
    else if(e.key==="End")next=n-1;
    if(next===null)return;
    e.preventDefault();
    setActive(next);
    tabRefs.current[next]?.focus();
  }

  if(!postcode)return <section data-testid="local-information-hub" className="rounded-2xl border border-white/10 bg-slate-900/60 p-6"><p className="text-xs font-bold uppercase tracking-[.2em] text-sky-300">{t("eyebrow")}</p><h2 className="mt-2 text-2xl font-bold">{t("introTitle")}</h2><p className="mt-2 max-w-3xl text-slate-400">{t("introBody")}</p></section>;

  if(status==="loading"&&!hub)return <section data-testid="local-information-hub" aria-live="polite" className="rounded-2xl border border-white/10 p-6">{t("loading")}</section>;

  if(status==="error"||!hub)return <section data-testid="local-information-hub" className="rounded-2xl border border-white/10 p-6"><div role="alert"><p className="text-sm text-rose-300">{t("error")}</p><p className="mt-1 text-xs text-slate-500">{t("errorHint")}</p></div></section>;

  if(status==="empty")return <section data-testid="local-information-hub" aria-live="polite" className="rounded-2xl border border-white/10 p-6">{t("empty")}</section>;

  const items=hub.items;
  const current=items[Math.min(active,items.length-1)];

  return <section data-testid="local-information-hub" aria-labelledby="local-hub-title" className="space-y-4">
    <header className="flex flex-wrap items-end justify-between gap-3"><div><p className="text-xs font-bold uppercase tracking-[.18em] text-sky-300">{t("briefingFor",{postcode:hub.postcode})}</p><h2 id="local-hub-title" className="mt-1 text-2xl font-bold">{t("todayIn",{locality:hub.locality})}</h2></div><span className="text-xs text-slate-500">{t("verifiedNote")}</span></header>
    <p className="sr-only">{t("chartFallback",{count:items.length})}</p>
    <div role="tablist" aria-label={t("topicsLabel")} className="flex flex-wrap gap-1.5">
      {items.map((item,idx)=><button key={item.id} ref={(el)=>{tabRefs.current[idx]=el}} role="tab" id={`hub-tab-${item.id}`} aria-selected={idx===active} aria-controls={`hub-panel-${item.id}`} tabIndex={idx===active?0:-1} onClick={()=>setActive(idx)} onKeyDown={(e)=>onTabKey(e,idx)} className={`rounded-lg border px-2.5 py-1.5 text-xs font-semibold transition-all ${idx===active?"border-sky-400/60 bg-sky-500/20 text-white":"border-white/10 bg-slate-800/60 text-slate-300 hover:border-sky-400/40"}`}><span aria-hidden> {icons[item.category]??"•"}</span> {item.category}{item.status==="source_pending"&&<span className="ml-1 rounded bg-slate-600/60 px-1 text-[10px] font-bold" title={t("pendingBadge")}>…</span>}</button>)}
    </div>
    {current&&<article key={current.id} role="tabpanel" id={`hub-panel-${current.id}`} aria-labelledby={`hub-tab-${current.id}`} className="flex min-h-52 flex-col rounded-2xl border border-white/10 bg-slate-900/70 p-4 shadow-lg shadow-black/10">
      <div className="flex items-start justify-between gap-3"><span className="text-2xl" aria-hidden>{icons[current.category]}</span><span className="flex items-center gap-2"><SourceTrustBadge state={trustOf(current)} source={current.source} refreshedAt={hub.generated_at}/><span className={`rounded-full px-2 py-1 text-[10px] font-bold ${current.importance==="urgent"?"bg-rose-500/20 text-rose-200":current.importance==="important"?"bg-amber-500/20 text-amber-200":"bg-slate-700 text-slate-300"}`}>{current.importance}</span></span></div>
      <h3 className="mt-3 text-base font-bold">{current.title}</h3><p className="mt-2 flex-1 text-sm leading-6 text-slate-400">{current.summary}</p>
      <div className="mt-4 flex items-center justify-between gap-2 border-t border-white/5 pt-3"><a href={current.source_url} target="_blank" rel="noreferrer" className="truncate text-xs text-sky-300">{t("source",{name:current.source})}</a><span className="flex shrink-0 gap-2"><button onClick={()=>{lastFocus.current=document.activeElement as HTMLElement|null;setDetail(current)}} className="rounded-lg border border-white/10 px-2 py-1 text-xs hover:bg-white/10">{t("title")}</button>{current.map_layer&&<button onClick={()=>onOpenMap?.(current.map_layer!)} className="shrink-0 rounded-lg border border-white/10 px-2 py-1 text-xs hover:bg-white/10">{t("openMap")}</button>}</span></div>
    </article>}
    {detail&&<div className="fixed inset-0 z-50 flex items-center justify-center bg-black/70 p-4" onClick={()=>setDetail(null)}><div role="dialog" aria-modal="true" aria-labelledby="hub-dialog-title" className="w-full max-w-lg rounded-2xl border border-white/10 bg-slate-900 p-5 shadow-2xl" onClick={(e)=>e.stopPropagation()}>
      <div className="flex items-start justify-between gap-3"><h3 id="hub-dialog-title" className="text-lg font-bold">{detail.title}</h3><button ref={closeBtnRef} onClick={()=>setDetail(null)} aria-label={t("close")} className="rounded-lg border border-white/10 px-2 py-1 text-xs hover:bg-white/10">✕</button></div>
      <p className="mt-2 text-sm leading-6 text-slate-300">{detail.summary}</p>
      <div className="mt-3 flex items-center gap-2"><SourceTrustBadge state={trustOf(detail)} source={detail.source} refreshedAt={hub.generated_at}/><a href={detail.source_url} target="_blank" rel="noreferrer" className="truncate text-xs text-sky-300">{t("source",{name:detail.source})}</a></div>
    </div></div>}
    <ResidentCivicPanels postcode={hub.postcode} />
    <p className="rounded-xl border border-sky-500/20 bg-sky-500/5 p-3 text-xs leading-5 text-slate-400">{hub.editorial_note}</p>
  </section>;
}
