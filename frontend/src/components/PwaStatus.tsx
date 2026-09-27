"use client";
import { useEffect, useState } from "react";
import { useTranslations } from "next-intl";

export default function PwaStatus() {
  const t = useTranslations("pwa.status");
  const [online, setOnline] = useState(true);
  useEffect(() => {
    setOnline(navigator.onLine);
    const onOnline = () => setOnline(true);
    const onOffline = () => setOnline(false);
    addEventListener("online", onOnline);
    addEventListener("offline", onOffline);
    if ("serviceWorker" in navigator) void navigator.serviceWorker.register("/sw.js");
    return () => {
      removeEventListener("online", onOnline);
      removeEventListener("offline", onOffline);
    };
  }, []);
  return (
    <span role="status" aria-live="polite" className={`rounded px-2 py-1 text-xs ${online ? "bg-emerald-500/20" : "bg-amber-500/20"}`}>
      {online ? t("online") : t("offline")}
    </span>
  );
}
