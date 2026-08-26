"use client";

import { useEffect, useRef, useState } from "react";
import * as maplibregl from "maplibre-gl";

// Audit B: a globális CSS-t a layout.tsx importálja (Next.js 14 warn fix)

const ZH_HB: [number, number] = [8.54, 47.378];
const SWISSTOPO_STYLE =
  "https://vectortiles.geo.admin.ch/styles/ch.swisstopo.lightbasemap.vt/style.json";

export default function Map({ lngLat }: { lngLat: [number, number] | null }) {
  const containerRef = useRef<HTMLDivElement>(null);
  const mapRef = useRef<maplibregl.Map | null>(null);
  const markerRef = useRef<maplibregl.Marker | null>(null);
  const [loadError, setLoadError] = useState<string | null>(null);

  useEffect(() => {
    if (!containerRef.current || mapRef.current) return;

    let map: maplibregl.Map | null = null;
    try {
      map = new maplibregl.Map({
        container: containerRef.current,
        style: SWISSTOPO_STYLE,
        center: ZH_HB,
        zoom: 12,
      });
    } catch (e) {
      setLoadError(e instanceof Error ? e.message : String(e));
      return;
    }

    map.addControl(new maplibregl.NavigationControl(), "top-right");

    map.on("error", (e) => {
      // MapLibre error — surface to UI instead of silent white screen
      const msg = (e as { error?: { message?: string } })?.error?.message ?? String(e.error ?? e);
      // eslint-disable-next-line no-console
      console.error("[Map] error", msg);
      setLoadError(msg);
    });

    map.on("load", () => {
      markerRef.current = new maplibregl.Marker({ color: "#0ea5e9" })
        .setLngLat(ZH_HB)
        .setPopup(new maplibregl.Popup().setText("Zürich HB — pilot"))
        .addTo(map!);
    });

    mapRef.current = map;
    return () => {
      map?.remove();
      mapRef.current = null;
      markerRef.current = null;
    };
  }, []);

  useEffect(() => {
    if (!lngLat || !mapRef.current || !markerRef.current) return;
    mapRef.current.flyTo({ center: lngLat, zoom: 14 });
    markerRef.current.setLngLat(lngLat);
  }, [lngLat]);

  return (
    <div
      data-testid="map-container"
      ref={containerRef}
      className="h-[60vh] min-h-[320px] w-full rounded-lg border overflow-hidden bg-zinc-100"
      style={{ minHeight: 320 }}
    >
      {loadError ? (
        <div
          data-testid="map-error"
          className="flex h-full w-full items-center justify-center p-4 text-sm text-amber-800 bg-amber-50"
        >
          Térkép betöltési hiba: {loadError}
        </div>
      ) : null}
    </div>
  );
}
