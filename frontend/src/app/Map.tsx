"use client";

import { useEffect, useRef } from "react";
import * as maplibregl from "maplibre-gl";
import "maplibre-gl/dist/maplibre-gl.css";

const ZH_HB: [number, number] = [8.54, 47.378];
const SWISSTOPO_STYLE =
  "https://vectortiles.geo.admin.ch/styles/ch.swisstopo.lightbasemap.vt/style.json";

export default function Map() {
  const containerRef = useRef<HTMLDivElement>(null);
  const mapRef = useRef<maplibregl.Map | null>(null);

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
      new maplibregl.Marker({ color: "#0ea5e9" })
        .setLngLat(ZH_HB)
        .setPopup(new maplibregl.Popup().setText("Zürich HB — pilot"))
        .addTo(map);
    });

    mapRef.current = map;
    return () => {
      map.remove();
      mapRef.current = null;
    };
  }, []);

  return <div ref={containerRef} className="h-[60vh] w-full rounded-lg border" />;
}
