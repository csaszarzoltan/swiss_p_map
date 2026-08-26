"use client";

import { useEffect, useRef } from "react";
import * as maplibregl from "maplibre-gl";

// Audit B: a globális CSS-t a layout.tsx importálja (Next.js 14 warn fix)
// A Map komponens így komponens-szinten már nem importál CSS-t.

const ZH_HB: [number, number] = [8.54, 47.378];
const SWISSTOPO_STYLE =
  "https://vectortiles.geo.admin.ch/styles/ch.swisstopo.lightbasemap.vt/style.json";

export default function Map({ lngLat }: { lngLat: [number, number] | null }) {
  const containerRef = useRef<HTMLDivElement>(null);
  const mapRef = useRef<maplibregl.Map | null>(null);
  const markerRef = useRef<maplibregl.Marker | null>(null);

  useEffect(() => {
    if (!containerRef.current || mapRef.current) return;

    const map = new maplibregl.Map({
      container: containerRef.current,
      style: SWISSTOPO_STYLE,
      center: ZH_HB,
      zoom: 12,
    });

    map.addControl(new maplibregl.NavigationControl(), "top-right");

    map.on("load", () => {
      markerRef.current = new maplibregl.Marker({ color: "#0ea5e9" })
        .setLngLat(ZH_HB)
        .setPopup(new maplibregl.Popup().setText("Zürich HB — pilot"))
        .addTo(map);
    });

    mapRef.current = map;
    return () => {
      map.remove();
      mapRef.current = null;
      markerRef.current = null;
    };
  }, []);

  useEffect(() => {
    if (!lngLat || !mapRef.current || !markerRef.current) return;
    mapRef.current.flyTo({ center: lngLat, zoom: 14 });
    markerRef.current.setLngLat(lngLat);
  }, [lngLat]);

  return <div ref={containerRef} className="h-[60vh] w-full rounded-lg border" />;
}
