"use client";

import { useEffect, useRef, useState } from "react";
import * as THREE from "three";
import { OrbitControls } from "three/addons/controls/OrbitControls.js";
import gsap from "gsap";
import { SWISS_CANTONS } from "./swissCantons";
import { SWISS_CITIES, SWISS_RIVERS, SWISS_LAKES, SWISS_ROADS } from "./mapOverlay";
import { CITY_OUTLINES } from "./cityOutlines";
import type { Baugesuch, PlaceInfo } from "@/lib/api";
import type { Topic } from "@/components/TopicSidebar";
import { lonLatToModel } from "./projection";


// 70°-os felülnézet + jobban bezoomolva (kameraszög ~69°, FOV 34°)
const INITIAL_CAM = { x: 0, y: 9.0, z: 3.2 };
const INITIAL_TARGET = { x: 0, y: 0, z: -0.15 };

const BASE_GLASS = { color: 0x1e293b, opacity: 0.42 };
const BASE_EDGE = 0x64748b;
const HOVER_EMISSIVE = 0x0284c7;

const SOLAR_DATA: Record<string, { kwh: number; rating: string }> = {
  VS: { kwh: 1420, rating: "Ausgezeichnet" },
  TI: { kwh: 1380, rating: "Ausgezeichnet" },
  GR: { kwh: 1350, rating: "Sehr gut" },
  GE: { kwh: 1290, rating: "Sehr gut" },
  VD: { kwh: 1270, rating: "Sehr gut" },
  ZH: { kwh: 1208, rating: "Gut" },
  BE: { kwh: 1190, rating: "Gut" },
  BS: { kwh: 1150, rating: "Gut" },
  LU: { kwh: 1180, rating: "Gut" },
  ZG: { kwh: 1220, rating: "Sehr gut" },
  SZ: { kwh: 1195, rating: "Gut" },
  AG: { kwh: 1170, rating: "Gut" },
  SG: { kwh: 1160, rating: "Gut" },
  SO: { kwh: 1175, rating: "Gut" },
  BL: { kwh: 1155, rating: "Gut" },
  FR: { kwh: 1210, rating: "Sehr gut" },
  JU: { kwh: 1140, rating: "Mäßig" },
  NE: { kwh: 1190, rating: "Gut" },
  SH: { kwh: 1185, rating: "Gut" },
  TG: { kwh: 1175, rating: "Gut" },
  UR: { kwh: 1250, rating: "Sehr gut" },
  OW: { kwh: 1230, rating: "Sehr gut" },
  NW: { kwh: 1240, rating: "Sehr gut" },
  GL: { kwh: 1210, rating: "Sehr gut" },
  AR: { kwh: 1150, rating: "Gut" },
  AI: { kwh: 1150, rating: "Gut" },
};

const OEREB_ZONES: Record<string, { zone: string; color: string }> = {
  ZH: { zone: "Wohnzone W3 / Kernzone", color: "#3b82f6" },
  BE: { zone: "UNESCO Altstadt / Wohnzone", color: "#ec4899" },
  BS: { zone: "Schonzone Altstadt / Gewerbe", color: "#f97316" },
  GE: { zone: "Zone de développement / Résidentiel", color: "#3b82f6" },
  VD: { zone: "Zone villa / Centre", color: "#3b82f6" },
  ZG: { zone: "Wohn- und Arbeitszone", color: "#f97316" },
  SZ: { zone: "Dorfzone / Landwirtschaft", color: "#22c55e" },
  LU: { zone: "Kernzone Altstadt", color: "#ec4899" },
  VS: { zone: "Tourismus- und Dorfzone", color: "#8b5cf6" },
  TI: { zone: "Zona residenziale intensiva", color: "#3b82f6" },
  GR: { zone: "Landschaftsschutzzone", color: "#22c55e" },
};

const OEV_CLASSES: Record<string, { cls: string; color: string; noise: number }> = {
  ZH: { cls: "A (sehr dicht)", color: "#10b981", noise: 62.5 },
  BE: { cls: "A (dicht)", color: "#10b981", noise: 59.0 },
  BS: { cls: "A (sehr dicht)", color: "#10b981", noise: 64.0 },
  GE: { cls: "A (sehr dicht)", color: "#10b981", noise: 63.5 },
  VD: { cls: "B (gut)", color: "#06b6d4", noise: 60.0 },
  LU: { cls: "A (dicht)", color: "#10b981", noise: 58.5 },
  ZG: { cls: "B (gut)", color: "#06b6d4", noise: 57.0 },
  SZ: { cls: "C (mittel)", color: "#8b5cf6", noise: 54.0 },
  VS: { cls: "D (mäßig)", color: "#f59e0b", noise: 52.0 },
  TI: { cls: "B (gut)", color: "#06b6d4", noise: 59.5 },
  GR: { cls: "D (mäßig)", color: "#f59e0b", noise: 50.0 },
};


// Kantonra zoom 70°-ra hangolva — szorosabb, mint az országos nézet
const CANTON_CAM_OFFSET = { y: 3.4, z: 1.22 };
const CITY_CAM_OFFSET = { y: 2.1, z: 0.76 };

function buildMesh(
  points: [number, number][],
  depth: number,
  data: Record<string, unknown>,
  isCity = false,
): THREE.Mesh {
  const shape = new THREE.Shape();
  shape.moveTo(points[0][0], points[0][1]);
  for (let i = 1; i < points.length; i++) shape.lineTo(points[i][0], points[i][1]);
  shape.closePath();
  const geom = new THREE.ExtrudeGeometry(shape, {
    depth,
    bevelEnabled: true,
    bevelSegments: 2,
    steps: 1,
    bevelSize: 0.03,
    bevelThickness: 0.03,
  });
  geom.computeBoundingBox();
  const mat = new THREE.MeshStandardMaterial({
    color: BASE_GLASS.color,
    roughness: 0.1,
    metalness: 0.05,
    transparent: true,
    opacity: isCity ? 0.58 : BASE_GLASS.opacity,
    polygonOffset: true,
    polygonOffsetFactor: 1,
    polygonOffsetUnits: 1,
  });
  const mesh = new THREE.Mesh(geom, mat);
  mesh.castShadow = true;
  mesh.receiveShadow = true;
  mesh.rotation.x = -Math.PI / 2;
  const edges = new THREE.EdgesGeometry(geom);
  const edgeMat = new THREE.LineBasicMaterial({ color: BASE_EDGE, transparent: true, opacity: 0.45 });
  const edgeLines = new THREE.LineSegments(edges, edgeMat);
  mesh.add(edgeLines);
  mesh.userData = {
    ...(data as object),
    baseY: isCity ? 0.35 : 0,
    edgeLines,
    isCity,
    origColor: BASE_GLASS.color,
    origOpacity: isCity ? 0.58 : BASE_GLASS.opacity,
  };
  if (isCity) mesh.position.y = 0.35;
  return mesh;
}

interface MapLocale {
  title: string;
  breadcrumb: string;
  subtitle: string;
  cantons: string;
  population: string;
  hint: string;
  compass: string;
  areaLabel: string;
  popLabel: string;
  voteYes: string;
  voteNo: string;
  support: string;
  cantonSubtitle: string;
  citySubtitle: string;
}

export default function Map3D(
  {
    selectedPostcode = null,
    placeInfo = null,
    activeTopic = "overview",
    onTopicChange,
    baugesuche = [],
    mapLocale,
  }: {
    selectedPostcode?: string | null;
    placeInfo?: PlaceInfo | null;
    activeTopic?: string;
    onTopicChange?: (topic: Topic) => void;
    baugesuche?: Baugesuch[];
    mapLocale?: MapLocale;
  } = {},

) {
  const ml: MapLocale = mapLocale ?? {
    title: "Schweizerische Eidgenossenschaft",
    breadcrumb: "SCHWEIZ",
    subtitle: "Bewege die Maus über einen Kanton für die 3D-Hervorhebung, dann klicke, um die Städte im Kanton zu entdecken!",
    cantons: "26 Kantone",
    population: "8.9 Millionen",
    hint: "Linke Taste: Drehen · Rechts: Schwenken · Rad: Zoom",
    compass: "N",
    areaLabel: "Gebiet / Einheit",
    popLabel: "Bevölkerung",
    voteYes: "JA",
    voteNo: "NEIN",
    support: "Zustimmung",
    cantonSubtitle: "Bezirksdaten geöffnet. Bewege die Maus über die Bezirke für Details!",
    citySubtitle: "Gemeindeweite Ergebnisse.",
  };
  const containerRef = useRef<HTMLDivElement>(null);
  const tooltipRef = useRef<HTMLDivElement>(null);
  const [breadcrumb, setBreadcrumb] = useState(() => ml.breadcrumb);
  const [title, setTitle] = useState(() => ml.title);
  const [subtitle, setSubtitle] = useState(() => ml.subtitle);
  const [statTarget, setStatTarget] = useState(() => ml.cantons);
  const [statPop, setStatPop] = useState(() => ml.population);
  const [voteYes, setVoteYes] = useState(58.2);
  const [activeCode, setActiveCode] = useState<string | null>(null);
  const [showBack, setShowBack] = useState(false);

  useEffect(() => {
    setBreadcrumb(ml.breadcrumb);
    setTitle(ml.title);
    setStatTarget(ml.cantons);
    setStatPop(ml.population);
  }, [ml.breadcrumb, ml.title, ml.cantons, ml.population]);

  useEffect(() => {
    if (activeTopic === "solar" || activeTopic === "sonnendach") {
      setSubtitle("BFE Sonnendach Solarpotenzial & mittlere Einstrahlung (kWh/m²/Jahr)");
    } else if (activeTopic === "politik") {
      setSubtitle("BFS Eidgenössische Abstimmungen & kantonale Stimmbeteiligung");
    } else if (activeTopic === "planung") {
      setSubtitle(`Baugesuche: ${baugesuche.length} aktiv im 20-Tage Fenster — Einsprachefrist`);
    } else if (activeTopic === "ort") {
      setSubtitle("ARE ÖV-Güteklassen (A–D), sonBASE Lärmkataster und kantonale Steuerfüsse");
    } else if (activeTopic === "oereb") {
      setSubtitle("Swisstopo ÖREB-Kataster: öffentlich-rechtliche Eigentumsbeschränkungen");
    } else {
      setSubtitle(ml.subtitle);
    }
  }, [activeTopic, baugesuche.length, ml.subtitle]);


  const stateRef = useRef<{
    selectedCanton: THREE.Mesh | null;
    selectedCity: THREE.Mesh | null;
    currentHovered: THREE.Mesh | null;
    mainGroup: THREE.Group | null;
    subGroup: THREE.Group | null;
    overlayGroup: THREE.Group | null;
    detailOverlay: THREE.Group | null;
    pinGroup: THREE.Group | null;
    camera: THREE.PerspectiveCamera | null;
    controls: OrbitControls | null;
    raycaster: THREE.Raycaster;
    mouse: THREE.Vector2;
  }>({
    selectedCanton: null,
    selectedCity: null,
    currentHovered: null,
    mainGroup: null,
    subGroup: null,
    overlayGroup: null,
    detailOverlay: null,
    pinGroup: null,
    camera: null,
    controls: null,
    raycaster: new THREE.Raycaster(),
    mouse: new THREE.Vector2(),
  });

  const tip = (
    d: { name: string; pop: string; yes: number; code?: string; id?: string; customHtml?: string } | null,
    x?: number,
    y?: number,
  ) => {
    const el = tooltipRef.current;
    if (!el) return;
    if (!d) {
      el.style.display = "none";
      return;
    }
    el.style.display = "block";
    if (x !== undefined) {
      el.style.left = x + "px";
      el.style.top = y + "px";
    }
    if (d.customHtml) {
      el.innerHTML = d.customHtml;
      return;
    }
    const code = String(d.code ?? d.id ?? "");
    if (activeTopic === "solar" || activeTopic === "sonnendach") {
      const solar = SOLAR_DATA[code] ?? { kwh: 1208, rating: "Gut" };
      el.innerHTML = `<strong>${d.name}</strong>${d.pop ? ` · ${d.pop}` : ""}<br/>☀ Solarpotenzial: <span style="color:#fbbf24;font-weight:700;">${solar.kwh} kWh/m²/Jahr (${solar.rating})</span>`;
    } else if (activeTopic === "politik") {

      el.innerHTML = `<strong>${d.name}</strong>${d.pop ? ` · ${d.pop}` : ""}<br/>🗳 13. AHV-Rente: <span style="color:#38bdf8;font-weight:700;">${d.yes}% ${ml.voteYes}</span>`;
    } else if (activeTopic === "planung") {
      el.innerHTML = `<strong>${d.name}</strong>${d.pop ? ` · ${d.pop}` : ""}<br/>🏗 Baugesuche: <span style="color:#818cf8;font-weight:700;">Amtsblatt Publikationen aktiv</span>`;
    } else if (activeTopic === "ort") {
      const o = OEV_CLASSES[code] ?? { cls: "A", color: "#10b981", noise: 60 };
      el.innerHTML = `<strong>${d.name}</strong>${d.pop ? ` · ${d.pop}` : ""}<br/>📍 ÖV: <span style="color:#34d399;font-weight:700;">Klasse ${o.cls}</span> · Lärm: <span style="color:#94a3b8;font-weight:700;">${o.noise} dB</span>`;
    } else if (activeTopic === "oereb") {
      const z = OEREB_ZONES[code] ?? { zone: "Wohnzone / Kernzone", color: "#3b82f6" };
      el.innerHTML = `<strong>${d.name}</strong>${d.pop ? ` · ${d.pop}` : ""}<br/>⚖ Kataster: <span style="color:#60a5fa;font-weight:700;">${z.zone}</span>`;
    } else {
      el.innerHTML = `<strong>${d.name}</strong>${d.pop ? ` · ${d.pop}` : ""}<br/><span style="color:#94a3b8;">${ml.cantons}</span>`;
    }
  };


  const applyHover = (mesh: THREE.Mesh) => {
    document.body.style.cursor = "pointer";
    const baseY = mesh.userData.baseY as number;
    gsap.to(mesh.position, { y: baseY + (mesh.userData.isCity ? 0.28 : 0.45), duration: 0.28, ease: "power2.out" });
    gsap.to((mesh.material as THREE.MeshStandardMaterial).color, { r: 0.22, g: 0.74, b: 0.97, duration: 0.2 });
    gsap.to(mesh.material as THREE.MeshStandardMaterial, { opacity: 0.82, duration: 0.2 });
    (mesh.material as THREE.MeshStandardMaterial).emissive.setHex(HOVER_EMISSIVE);
    (mesh.material as THREE.MeshStandardMaterial).emissiveIntensity = 0.45;
    const _el1 = (mesh.userData.edgeLines as THREE.LineSegments).material as THREE.LineBasicMaterial;
    _el1.color.setHex(0xe0f2fe);
    _el1.opacity = 0.95;
    tip(mesh.userData as { name: string; pop: string; yes: number });
    const d = mesh.userData as { name: string; pop: string; yes: number; code?: string; id?: string };
    setStatTarget(d.name);
    setStatPop(d.pop);
    setVoteYes(d.yes);
    if (d.code || d.id) {
      setActiveCode(String(d.code ?? d.id));
    }
  };


  const resetHover = (mesh: THREE.Mesh) => {
    document.body.style.cursor = "default";
    tip(null);
    gsap.to(mesh.position, { y: mesh.userData.baseY as number, duration: 0.25, ease: "power2.out" });
    const orig = new THREE.Color(mesh.userData.origColor as number);
    gsap.to((mesh.material as THREE.MeshStandardMaterial).color, { r: orig.r, g: orig.g, b: orig.b, duration: 0.25 });
    gsap.to(mesh.material as THREE.MeshStandardMaterial, {
      opacity: mesh.userData.origOpacity as number,
      duration: 0.25,
    });
    (mesh.material as THREE.MeshStandardMaterial).emissive.setHex(0x000000);
    (mesh.material as THREE.MeshStandardMaterial).emissiveIntensity = 0;
    const _el2 = (mesh.userData.edgeLines as THREE.LineSegments).material as THREE.LineBasicMaterial;
    _el2.color.setHex(BASE_EDGE);
    _el2.opacity = 0.45;
  };

  const handleBack = () => {
    const s = stateRef.current;
    if (s.selectedCity) {
      s.selectedCity = null;
      const box = new THREE.Box3().setFromObject(s.selectedCanton as THREE.Object3D);
      const center = new THREE.Vector3();
      box.getCenter(center);
      gsap.to(s.camera!.position, { x: center.x, y: center.y + CANTON_CAM_OFFSET.y, z: center.z + CANTON_CAM_OFFSET.z, duration: 1.0, ease: "power2.inOut" });
      gsap.to(s.controls!.target, { x: center.x, y: center.y, z: center.z, duration: 1.0, ease: "power2.inOut" });
      s.subGroup!.children.forEach((cm) => {
        gsap.to((cm as THREE.Mesh).material as THREE.MeshStandardMaterial, { opacity: 0.34, duration: 0.4 });
      });
      setBreadcrumb(`${ml.breadcrumb} / ${(s.selectedCanton!.userData as { name: string }).name.toUpperCase()}`);
      setTitle((s.selectedCanton!.userData as { name: string }).name);
      setSubtitle(ml.cantonSubtitle);
      const d = s.selectedCanton!.userData as { name: string; pop: string; yes: number };
      setStatTarget(d.name);
      setStatPop(d.pop);
      setVoteYes(d.yes);
    } else if (s.selectedCanton) {
      const prevCanton = s.selectedCanton;
      s.selectedCanton = null;
      s.subGroup!.clear();
      s.subGroup!.visible = false;
      s.mainGroup!.visible = true;
      s.overlayGroup!.visible = true;
      // topológia visszaállítás országos opacitásra
      if (s.detailOverlay) {
        s.detailOverlay.children.forEach((obj) => {
          const mat = (obj as THREE.Line).material as THREE.LineBasicMaterial;
          if (mat.color.getHex() === 0x64748b) gsap.to(mat, { opacity: 0.28, duration: 0.4 });
          else if (mat.color.getHex() === 0x475569) gsap.to(mat, { opacity: 0.32, duration: 0.4 });
          else if (mat.color.getHex() === 0x334155) gsap.to(mat, { opacity: 0.22, duration: 0.4 });
        });
      }
      if (s.overlayGroup) {
        s.overlayGroup.children.forEach((obj) => {
          if ((obj as THREE.Mesh).isMesh) {
            const mm = (obj as THREE.Mesh).material as THREE.MeshStandardMaterial;
            if (mm.color?.getHex() === 0x1e40af) gsap.to(mm, { opacity: 0.35, duration: 0.4 });
          } else if ((obj as THREE.Line).isLine) {
            const lm = (obj as THREE.Line).material as THREE.LineBasicMaterial;
            if (lm.color.getHex() === 0x3b82f6) gsap.to(lm, { opacity: 0.7, duration: 0.4 });
          }
        });
      }
      // restore other cantons
      s.mainGroup!.children.forEach((c) => {
        c.visible = true;
        gsap.to(c.position, { y: 0, duration: 0.55 });
        gsap.to((c as THREE.Mesh).material as THREE.MeshStandardMaterial, { opacity: 0.42, duration: 0.55 });
      });
      // ensure selected canton mesh itself is visible again
      prevCanton.visible = true;
      gsap.to(s.camera!.position, { x: INITIAL_CAM.x, y: INITIAL_CAM.y, z: INITIAL_CAM.z, duration: 1.15, ease: "power2.inOut" });
      gsap.to(s.controls!.target, { x: INITIAL_TARGET.x, y: INITIAL_TARGET.y, z: INITIAL_TARGET.z, duration: 1.15, ease: "power2.inOut" });
      setBreadcrumb(ml.breadcrumb);
      setTitle(ml.title);
      setSubtitle(ml.subtitle);
      setStatTarget(ml.cantons);
      setStatPop(ml.population);
      setVoteYes(61.4);
      setShowBack(false);
    }
  };

  useEffect(() => {
    const container = containerRef.current;
    if (!container) return;

    const scene = new THREE.Scene();
    scene.fog = new THREE.FogExp2(0x030712, 0.022);
    const camera = new THREE.PerspectiveCamera(34, container.clientWidth / container.clientHeight, 0.1, 1000);
    camera.position.set(INITIAL_CAM.x, INITIAL_CAM.y, INITIAL_CAM.z);
    const renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true });
    renderer.setSize(container.clientWidth, container.clientHeight);
    renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
    renderer.shadowMap.enabled = true;
    renderer.shadowMap.type = THREE.PCFSoftShadowMap;
    container.appendChild(renderer.domElement);

    const controls = new OrbitControls(camera, renderer.domElement);
    controls.enableDamping = true;
    controls.dampingFactor = 0.05;
    controls.target.set(INITIAL_TARGET.x, INITIAL_TARGET.y, INITIAL_TARGET.z);
    controls.maxPolarAngle = Math.PI / 2.05;
    controls.minDistance = 1.2;
    controls.maxDistance = 26;
    controls.enablePan = true;

    scene.add(new THREE.AmbientLight(0xffffff, 0.7));
    const dl1 = new THREE.DirectionalLight(0xffffff, 1.05);
    dl1.position.set(10, 22, 14);
    dl1.castShadow = true;
    dl1.shadow.mapSize.set(2048, 2048);
    scene.add(dl1);
    const dl2 = new THREE.DirectionalLight(0x38bdf8, 0.5);
    dl2.position.set(-14, 12, -10);
    scene.add(dl2);
    const fill = new THREE.DirectionalLight(0x94a3b8, 0.35);
    fill.position.set(0, 8, -12);
    scene.add(fill);
    const grid = new THREE.GridHelper(36, 36, 0x1e293b, 0x0f172a);
    grid.position.y = -0.07;
    grid.material.opacity = 0.55;
    (grid.material as THREE.LineBasicMaterial).transparent = true;
    scene.add(grid);

    const mainGroup = new THREE.Group();
    const subGroup = new THREE.Group();
    subGroup.visible = false;
    scene.add(mainGroup);
    scene.add(subGroup);
    const overlayGroup = new THREE.Group();
    overlayGroup.position.y = 0.01;
    scene.add(overlayGroup);
    const pinGroup = new THREE.Group();
    pinGroup.position.y = 0.2;
    scene.add(pinGroup);

    stateRef.current.mainGroup = mainGroup;
    stateRef.current.subGroup = subGroup;
    stateRef.current.overlayGroup = overlayGroup;
    stateRef.current.pinGroup = pinGroup;
    stateRef.current.camera = camera;
    stateRef.current.controls = controls;

    SWISS_CANTONS.forEach((canton) => {
      const mesh = buildMesh(canton.points as [number, number][], 0.35, canton as unknown as Record<string, unknown>, false);
      mainGroup.add(mesh);
    });

    // Tavak — csillogó, áttetsző vízkék fényű anyag (Swiss Lakes)
    SWISS_LAKES.forEach((lake) => {
      const shape = new THREE.Shape();
      shape.moveTo(lake.pts[0][0], lake.pts[0][1]);
      for (let i = 1; i < lake.pts.length; i++) shape.lineTo(lake.pts[i][0], lake.pts[i][1]);
      shape.closePath();
      const geom = new THREE.ExtrudeGeometry(shape, { depth: 0.015, bevelEnabled: false });
      const mat = new THREE.MeshStandardMaterial({
        color: 0x06b6d4,
        emissive: 0x0284c7,
        emissiveIntensity: 0.4,
        transparent: true,
        opacity: 0.72,
        roughness: 0.1,
        metalness: 0.6,
      });
      const mesh = new THREE.Mesh(geom, mat);
      mesh.rotation.x = -Math.PI / 2;
      mesh.position.y = 0.005;
      overlayGroup.add(mesh);
    });
    // Folyók — kék vonalak
    SWISS_RIVERS.forEach((river) => {
      const pts3d = river.pts.map(([x, y]) => new THREE.Vector3(x, 0.02, -y));
      const geom = new THREE.BufferGeometry().setFromPoints(pts3d);
      const mat = new THREE.LineBasicMaterial({ color: 0x3b82f6, transparent: true, opacity: 0.7, linewidth: 2 });
      const line = new THREE.Line(geom, mat);
      overlayGroup.add(line);
    });
    // Városjelölők — kis oszlopok + pont felett
    SWISS_CITIES.forEach((city) => {
      const [cx, cy] = city.pts;
      // oszlop (gyűrű nélkül, vékony)
      const cyl = new THREE.Mesh(
        new THREE.CylinderGeometry(0.035, 0.035, 0.15, 12),
        new THREE.MeshStandardMaterial({ color: 0xf59e0b, emissive: 0xb45309, emissiveIntensity: 0.35 }),
      );
      cyl.position.set(cx, 0.08, -cy);
      overlayGroup.add(cyl);
      // pont korona
      const dot = new THREE.Mesh(
        new THREE.SphereGeometry(0.04, 10, 10),
        new THREE.MeshStandardMaterial({ color: 0xfbbf24, emissive: 0xf59e0b, emissiveIntensity: 0.6 }),
      );
      dot.position.set(cx, 0.17, -cy);
      overlayGroup.add(dot);
    });

    // Kantonon belül is halványan megmaradó részletek — külön csoport (nem tűnik el izoláláskor)
    const detailOverlay = new THREE.Group();
    detailOverlay.position.y = 0.012;
    scene.add(detailOverlay);
    stateRef.current.detailOverlay = detailOverlay;

    // Város-körvonalak (halvány vonalak) — minden kanton legnagyobb gemeindéi, országos nézetben szürke héj
    CITY_OUTLINES.forEach((city) => {
      const pts = city.pts.map(([x, y]) => new THREE.Vector3(x, 0.015, -y));
      pts.push(pts[0].clone());
      const geom = new THREE.BufferGeometry().setFromPoints(pts);
      const mat = new THREE.LineBasicMaterial({ color: 0x64748b, transparent: true, opacity: 0.28, linewidth: 1 });
      const line = new THREE.Line(geom, mat);
      line.userData = { ktnr: city.ktnr, name: city.name };
      detailOverlay.add(line);
    });
    // Főutak (A1/A2/A3/A9) — halvány szürke szaggatott benyomás
    SWISS_ROADS.forEach((road) => {
      const pts = road.pts.map(([x, y]) => new THREE.Vector3(x, 0.018, -y));
      const geom = new THREE.BufferGeometry().setFromPoints(pts);
      const mat = new THREE.LineBasicMaterial({ color: 0x475569, transparent: true, opacity: 0.32, linewidth: 1 });
      const line = new THREE.Line(geom, mat);
      detailOverlay.add(line);
    });
    // Hegyek — halvány domborzat-háló (procedurális ridges, nem pontos DEM, de felismerhető Alpok-tónus)
    const ridgePts: [number, number][][] = [
      // Berner Oberland / Wallis Alpok fő gerince
      [[7.6, 46.55],[7.7,46.52],[7.85,46.45],[7.95,46.38],[8.05,46.30],[8.20,46.25],[8.35,46.15],[8.50,46.05],[8.80,46.00],[9.10,46.10],[9.30,46.25],[9.45,46.40]],
      // Graubünden gerinc
      [[9.10,46.50],[9.25,46.55],[9.40,46.62],[9.55,46.72],[9.70,46.80],[9.90,46.85],[10.10,46.95]],
      // Jura vonal
      [[6.20,46.60],[6.40,46.75],[6.60,46.95],[6.90,47.10],[7.20,47.20],[7.45,47.35]],
    ];
    ridgePts.forEach((ring) => {
      // vetítés már lon/lat -> model x,y-ben van a ring? Itt lon/lat nyers: vetíteni kell mint a városoknál
      // cityOutlines vetítése már megtörtént — hegyekhez ugyanaz a pj függvény kellene; itt manuálisan projektálok:
      // Egyszerű: használom a már meglévő SWISS_CANTONS egy pontjának vetítési arányát reverse-engineerelve?
      // Helyette: a ring lon/lat-ja már pj nélkül van megadva a SWISS_ROADS-hoz hasonlóan lon/lat -> model.
      // Reuse: a városokhoz használt pj-t lemásolom lokálisan
      // For mountain we already stored as lon/lat pairs pre-projection in code comment below — project here inline
      // For simplicity treat ring entries as already-projected model pts via rough linear map (good enough for faint ridges)
      const projected = ring.map(([lon, lat]) => {
        // linear approx: lon 5.9..10.5 -> x -3.8..3.8, lat 45.8..47.8 -> y -2.5..2.5 scaled by earlier factor
        // Use same factor as mapOverlay: cosLat=0.685, scaleZoom=3.059
        const cosLat = Math.cos((46.8 * Math.PI) / 180);
        const rawW = (10.493446773955753 - 5.956800664952974) * cosLat;
        const rawH = 47.80743900893902 - 45.81913730594624;
        const scaleZoom = Math.min(9.5 / rawW, 6.2 / rawH);
        const cx = ((5.956800664952974 + 10.493446773955753) / 2) * cosLat;
        const cy = (45.81913730594624 + 47.80743900893902) / 2;
        return [(lon * cosLat - cx) * scaleZoom, (lat - cy) * scaleZoom] as [number, number];
      });
      const pts3 = projected.map(([x, y]) => new THREE.Vector3(x, 0.025, -y));
      const geom = new THREE.BufferGeometry().setFromPoints(pts3);
      const mat = new THREE.LineBasicMaterial({ color: 0x334155, transparent: true, opacity: 0.22, linewidth: 1 });
      const line = new THREE.Line(geom, mat);
      // halvány árnyék-glow mellé kis pufferek
      detailOverlay.add(line);
    });

    const onMouseMove = (e: MouseEvent) => {
      const rect = container.getBoundingClientRect();
      stateRef.current.mouse.x = ((e.clientX - rect.left) / rect.width) * 2 - 1;
      stateRef.current.mouse.y = -((e.clientY - rect.top) / rect.height) * 2 + 1;
      const tel = tooltipRef.current;
      if (tel && tel.style.display === "block") {
        tel.style.left = e.clientX + "px";
        tel.style.top = e.clientY + "px";
      }
      stateRef.current.raycaster.setFromCamera(stateRef.current.mouse, camera);
      const s = stateRef.current;

      // 1. Check 3D Baugesuch pins first (ADR-013)
      if (s.pinGroup && s.pinGroup.children.length > 0) {
        const pinHits = stateRef.current.raycaster.intersectObjects(s.pinGroup.children, true);
        if (pinHits.length > 0) {
          let pObj: THREE.Object3D | null = pinHits[0].object;
          while (pObj && !pObj.userData?.baugesuch && pObj.parent) {
            pObj = pObj.parent;
          }
          if (pObj?.userData?.baugesuch) {
            const bg = pObj.userData.baugesuch as Baugesuch;
            document.body.style.cursor = "pointer";
            tip({
              name: bg.title,
              pop: bg.municipality,
              yes: 0,
              customHtml: `<strong>🏗 ${bg.title}</strong><br/><span style="color:#fbbf24;font-size:11px;font-weight:600;">PLZ ${bg.postcode} ${bg.municipality} · ${bg.auflage_end ? `Auflage bis ${bg.auflage_end}` : "Aktiv"}</span>`,
            });
            return;
          }
        }
      }

      const targets = s.selectedCanton ? subGroup.children : mainGroup.children;
      const hits = stateRef.current.raycaster.intersectObjects(targets as THREE.Object3D[], false);
      if (hits.length > 0) {
        const hit = hits[0].object as THREE.Mesh;
        if (s.currentHovered !== hit) {
          if (s.currentHovered) resetHover(s.currentHovered);
          s.currentHovered = hit;
          applyHover(hit);
        }
      } else if (s.currentHovered) {
        resetHover(s.currentHovered);
        s.currentHovered = null;
      }
    };

    const onClick = () => {
      const s = stateRef.current;

      // 1. Click on 3D Baugesuch pin (ADR-013)
      if (s.pinGroup && s.pinGroup.children.length > 0) {
        const pinHits = stateRef.current.raycaster.intersectObjects(s.pinGroup.children, true);
        if (pinHits.length > 0) {
          let pObj: THREE.Object3D | null = pinHits[0].object;
          while (pObj && !pObj.userData?.baugesuch && pObj.parent) {
            pObj = pObj.parent;
          }
          if (pObj?.userData?.baugesuch) {
            const bg = pObj.userData.baugesuch as Baugesuch;
            setTitle(bg.title);
            setSubtitle(
              `Baugesuch ${bg.postcode} ${bg.municipality} — ${bg.auflage_end ? `Einsprachefrist bis ${bg.auflage_end}` : "Aktiv im 20-Tage Fenster"}`,
            );
            setStatTarget(`${bg.postcode} ${bg.municipality}`);
            setStatPop("Bauprojekt");
            return;
          }
        }
      }

      if (!s.currentHovered) return;
      let data = s.currentHovered.userData as {
        isCity?: boolean;
        cities?: { points: [number, number][]; name: string; pop: string; yes: number; id: string }[];
        districts?: { points: [number, number][]; name: string; pop: string; yes: number; id: string }[];
        name: string;
      };
      if (s.selectedCanton && data.isCity && !s.selectedCity) {
        s.selectedCity = s.currentHovered;
        const box = new THREE.Box3().setFromObject(s.selectedCity as unknown as THREE.Object3D);
        const center = new THREE.Vector3();
        box.getCenter(center);
        gsap.to(camera.position, { x: center.x, y: center.y + CITY_CAM_OFFSET.y, z: center.z + CITY_CAM_OFFSET.z, duration: 1.1, ease: "power3.inOut" });
        gsap.to(controls.target, { x: center.x, y: center.y, z: center.z, duration: 1.1, ease: "power3.inOut" });
        subGroup.children.forEach((cm) => {
          if (cm !== s.selectedCity) gsap.to((cm as THREE.Mesh).material as THREE.MeshStandardMaterial, { opacity: 0.12, duration: 0.4 });
        });
        setBreadcrumb(`${ml.breadcrumb} / ${(s.selectedCanton.userData as { name: string }).name.toUpperCase()} / ${data.name.toUpperCase()}`);
        setTitle(data.name);
        setSubtitle(ml.citySubtitle);
        return;
      }
      // Kanton szintre lépés — izolálás + Wahlkreis-darabolás
      if (!s.selectedCanton && !data.isCity) {
        const clicked = s.currentHovered;
        const clickedData = clicked.userData as typeof data;
        data = clickedData;
        resetHover(clicked);
        s.currentHovered = null;
        s.selectedCanton = clicked;
        const box = new THREE.Box3().setFromObject(s.selectedCanton as unknown as THREE.Object3D);
        const center = new THREE.Vector3();
        box.getCenter(center);
        // 70° pitch megtartása, közelebb zoom
        gsap.to(camera.position, { x: center.x, y: center.y + CANTON_CAM_OFFSET.y, z: center.z + CANTON_CAM_OFFSET.z, duration: 1.25, ease: "power3.inOut" });
        gsap.to(controls.target, { x: center.x, y: center.y, z: center.z, duration: 1.25, ease: "power3.inOut" });
        // többi kanton elsüllyed és eltűnik, kiválasztott is eltűnik (districtek veszik át)
        mainGroup.children.forEach((c) => {
          if (c !== s.selectedCanton) {
            gsap.to(c.position, { y: -0.9, duration: 0.45 });
            gsap.to((c as THREE.Mesh).material as THREE.MeshStandardMaterial, {
              opacity: 0,
              duration: 0.45,
              onComplete: () => {
                c.visible = false;
              },
            });
          } else {
            gsap.to((c as THREE.Mesh).material as THREE.MeshStandardMaterial, {
              opacity: 0,
              duration: 0.35,
              onComplete: () => {
                c.visible = false;
                mainGroup.visible = false;
                s.overlayGroup!.visible = false;
              },
            });
          }
        });
        tip(null);
        subGroup.clear();
        subGroup.visible = true;
        // detailOverlay marad látható — város-körvonalak/utak halványan a Wahlkreisek alatt
        const source =
          (data.districts?.length ? data.districts : data.cities) as
            | { points: [number, number][]; name: string; pop: string; yes: number; id: string }[]
            | undefined;
        if (source?.length) {
          source.forEach((item, idx) => {
            const m = buildMesh(item.points, 0.22, item as unknown as Record<string, unknown>, true);
            // kisebb kiemelés + hézag: topológia alatta jobban látszik
            const tmpBox = new THREE.Box3().setFromObject(m);
            const tmpCenter = new THREE.Vector3();
            tmpBox.getCenter(tmpCenter);
            const dir = tmpCenter.clone().sub(center);
            dir.y = 0;
            if (dir.lengthSq() > 1e-6) {
              dir.normalize().multiplyScalar(0.05);
              m.position.x += dir.x;
              m.position.z += dir.z;
            }
            m.userData.baseY = 0.14;
            m.position.y = 0.14;
            (m.material as THREE.MeshStandardMaterial).opacity = 0;
            (m.material as THREE.MeshStandardMaterial).transparent = true;
            subGroup.add(m);
            gsap.to(m.scale, { x: 1, y: 1, z: 1, duration: 0.52, delay: idx * 0.045, ease: "back.out(1.5)" });
            gsap.to(m.material as THREE.MeshStandardMaterial, { opacity: 0.34, duration: 0.42, delay: idx * 0.045 });
          });
          // kantonon belül: város-körvonalak + utak + hegyek megerősítése (topológia előtérbe)
          const dl = stateRef.current.detailOverlay!;
          dl.children.forEach((obj) => {
            const line = obj as THREE.Line;
            const mat = line.material as THREE.LineBasicMaterial;
            if (mat.color.getHex() === 0x64748b) gsap.to(mat, { opacity: 0.62, duration: 0.4 }); // város-körvonal
            else if (mat.color.getHex() === 0x475569) gsap.to(mat, { opacity: 0.55, duration: 0.4 }); // út
            else if (mat.color.getHex() === 0x334155) gsap.to(mat, { opacity: 0.40, duration: 0.4 }); // hegy
          });
          // rivers/lakes/city markers: ne tüntesd el, csak halványítsd — topológia referencia maradjon
          const ol = stateRef.current.overlayGroup!;
          ol.children.forEach((obj) => {
            if ((obj as THREE.Mesh).isMesh) {
              const mm = (obj as THREE.Mesh).material as THREE.MeshStandardMaterial;
              if (mm.color?.getHex() === 0x1e40af) gsap.to(mm, { opacity: 0.22, duration: 0.4 }); // tó
            } else if ((obj as THREE.Line).isLine) {
              const lm = (obj as THREE.Line).material as THREE.LineBasicMaterial;
              if (lm.color.getHex() === 0x3b82f6) gsap.to(lm, { opacity: 0.45, duration: 0.4 }); // folyó marad
            }
          });
        }
        setBreadcrumb(`SVÁJC / ${data.name.toUpperCase()}`);
        setTitle(`${data.name} kanton`);
        setSubtitle("Választási körzetek (Wahlkreis) szerint szétbontva — vidd az egeret egy körzet fölé!");
        setShowBack(true);
        return;
      }
    };

    window.addEventListener("mousemove", onMouseMove);
    window.addEventListener("click", onClick);

    let raf = 0;
    const animate = () => {
      raf = requestAnimationFrame(animate);
      controls.update();
      renderer.render(scene, camera);
    };
    animate();

    const onResize = () => {
      camera.aspect = container.clientWidth / container.clientHeight;
      camera.updateProjectionMatrix();
      renderer.setSize(container.clientWidth, container.clientHeight);
    };
    window.addEventListener("resize", onResize);

    return () => {
      cancelAnimationFrame(raf);
      window.removeEventListener("mousemove", onMouseMove);
      window.removeEventListener("click", onClick);
      window.removeEventListener("resize", onResize);
      controls.dispose();
      renderer.dispose();
      container.removeChild(renderer.domElement);
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  // 3D Baugesuch pins — selectedPostcode + baugesuche → pinGroup (amber pins)
  useEffect(() => {
    const pg = stateRef.current.pinGroup;
    if (!pg) return;
    pg.clear();
    if (baugesuche.length === 0) return;
    for (const b of baugesuche) {
      if (b.lat == null || b.lon == null) continue;
      const [x, y] = lonLatToModel(b.lon, b.lat);
      const pin = new THREE.Group();
      pin.position.set(x, 0.28, -y);
      const stem = new THREE.Mesh(
        new THREE.CylinderGeometry(0.012, 0.012, 0.14, 8),
        new THREE.MeshStandardMaterial({ color: 0xf59e0b, emissive: 0xb45309, emissiveIntensity: 0.45 }),
      );
      stem.position.y = 0.07;
      pin.add(stem);
      const head = new THREE.Mesh(
        new THREE.SphereGeometry(0.035, 12, 12),
        new THREE.MeshStandardMaterial({ color: 0xfbbf24, emissive: 0xf59e0b, emissiveIntensity: 0.7 }),
      );
      head.position.y = 0.16;
      pin.add(head);
      // subtle glow ring at base
      const ring = new THREE.Mesh(
        new THREE.RingGeometry(0.04, 0.06, 16),
        new THREE.MeshBasicMaterial({ color: 0xf59e0b, transparent: true, opacity: 0.35, side: THREE.DoubleSide }),
      );
      ring.rotation.x = -Math.PI / 2;
      ring.position.y = -0.06;
      pin.add(ring);
      pin.userData = { baugesuch: b };
      pg.add(pin);
      // pulse animation
      gsap.to(head.scale, { x: 1.18, y: 1.18, z: 1.18, duration: 0.9, yoyo: true, repeat: -1, ease: "sine.inOut" });
    }
    // highlight postcode badge when pins exist
    if (selectedPostcode) {
      setSubtitle(`Baugesuche: ${baugesuche.length} aktiv im 20-Tage Fenster — Einsprache möglich`);
    }
  }, [baugesuche, selectedPostcode]);

  // Pins visibility based on activeTopic
  useEffect(() => {
    const pg = stateRef.current.pinGroup;
    if (!pg) return;
    pg.visible = activeTopic === "planung" || activeTopic === "overview";
  }, [activeTopic]);

  useEffect(() => {
    const tax: Record<string, number> = { ZG: 54, SZ: 60, NW: 65, ZH: 119, LU: 116, BE: 154, NE: 156, GE: 155 };
    const prices: Record<string, number> = { ZG: 15300, GE: 14200, ZH: 12500, SZ: 11600, BS: 10300, VD: 9800, BE: 7600, TI: 7200 };

    stateRef.current.mainGroup?.children.forEach((child) => {
      const mesh = child as THREE.Mesh;
      const material = mesh.material as THREE.MeshStandardMaterial;
      const code = String(mesh.userData.code ?? mesh.userData.id ?? "");
      let color = new THREE.Color(BASE_GLASS.color);
      let opacity = BASE_GLASS.opacity;

      if (activeTopic === "solar" || activeTopic === "sonnendach") {
        const solar = SOLAR_DATA[code] ?? { kwh: 1180, rating: "Gut" };
        const hex = solar.kwh >= 1350 ? "#fbbf24" : solar.kwh >= 1220 ? "#f59e0b" : solar.kwh >= 1160 ? "#eab308" : "#ca8a04";
        color = new THREE.Color(hex);
        opacity = 0.65;
      } else if (activeTopic === "politik") {
        const yes = (mesh.userData.yes as number) ?? 52.0;
        const hex = yes >= 55 ? "#38bdf8" : yes >= 50 ? "#0284c7" : yes >= 45 ? "#f43f5e" : "#be123c";
        color = new THREE.Color(hex);
        opacity = 0.65;
      } else if (activeTopic === "planung") {
        color = new THREE.Color("#4f46e5");
        opacity = 0.55;
      } else if (activeTopic === "ort") {
        const oev = OEV_CLASSES[code] ?? { cls: "B", color: "#06b6d4", noise: 60 };
        color = new THREE.Color(oev.color);
        opacity = 0.60;
      } else if (activeTopic === "oereb") {
        const z = OEREB_ZONES[code] ?? { zone: "Wohnzone", color: "#3b82f6" };
        color = new THREE.Color(z.color);
        opacity = 0.60;
      } else {
        // overview
        color = new THREE.Color(BASE_GLASS.color);
        opacity = BASE_GLASS.opacity;
      }

      mesh.userData.origColor = color.getHex();
      mesh.userData.origOpacity = opacity;
      gsap.to(material.color, { r: color.r, g: color.g, b: color.b, duration: 0.45, ease: "power2.out" });
      gsap.to(material, { opacity, duration: 0.45, ease: "power2.out" });
    });
  }, [activeTopic]);

  const noPct = (100 - voteYes).toFixed(1);
  const currentCode = activeCode ?? placeInfo?.canton ?? "ZH";
  const currentSolar = SOLAR_DATA[currentCode] ?? { kwh: placeInfo?.solar_kwh_m2 ?? 1208, rating: placeInfo?.solar_class ?? "Sehr gut" };
  const currentOev = OEV_CLASSES[currentCode] ?? { cls: placeInfo?.oev_class ?? "A", color: "#10b981", noise: placeInfo?.noise_db_day ?? 62.5 };
  const currentOereb = OEREB_ZONES[currentCode] ?? { zone: placeInfo?.oereb_zone ?? "Wohnzone W3 / Kernzone", color: "#3b82f6" };
  const cantonTax: Record<string, number> = { ZG: 54, SZ: 60, NW: 65, OW: 68, UR: 85, LU: 116, ZH: 119, AG: 112, SG: 115, BE: 154, NE: 156, GE: 155, VD: 148, BS: 130, BL: 135 };
  const currentTax = cantonTax[currentCode] ?? placeInfo?.steuerfuss_percent ?? 119;

  return (
    <div className="relative w-full overflow-hidden rounded-xl border border-white/10" style={{ height: "62vh", minHeight: 380, background: "radial-gradient(circle at 50% 30%, #111827 0%, #030712 100%)" }} data-testid="map-3d">
      <div ref={containerRef} className="absolute inset-0" data-testid="map-3d-canvas" />
      
      {/* 3D Map Thematic Layer Selector */}
      <div data-testid="map-layer-selector" className="absolute right-3 top-3 z-30 flex flex-wrap gap-1 rounded-xl border border-white/15 bg-slate-950/85 p-1 backdrop-blur-md shadow-lg">
        {[
          { id: "overview" as Topic, label: "Übersicht" },
          { id: "politik" as Topic, label: "Politik" },
          { id: "planung" as Topic, label: "Planung" },
          { id: "solar" as Topic, label: "Sonnendach" },
          { id: "ort" as Topic, label: "Ort" },
          { id: "oereb" as Topic, label: "ÖREB" },
        ].map((t) => (
          <button
            key={t.id}
            onClick={() => onTopicChange?.(t.id)}
            aria-pressed={activeTopic === t.id || (t.id === "solar" && activeTopic === "sonnendach")}
            className={`rounded-lg px-2.5 py-1 text-[11px] font-semibold transition-all ${
              activeTopic === t.id || (t.id === "solar" && activeTopic === "sonnendach")
                ? "bg-sky-500 text-white shadow-sm"
                : "text-slate-300 hover:bg-white/10 hover:text-white"
            }`}
          >
            {t.label}
          </button>
        ))}
      </div>

      {/* Iránytű */}
      <div className="pointer-events-none absolute right-4 top-14 z-10 flex h-11 w-11 flex-col items-center justify-center rounded-full border border-white/10 bg-[rgba(17,24,39,0.7)] shadow-[0_4px_20px_rgba(0,0,0,0.4)] backdrop-blur-[12px]">
        <div className="mb-0.5 h-0 w-0 border-x-[5px] border-b-[9px] border-x-transparent border-b-[#38bdf8]" />
        <span className="text-[10px] font-bold text-[#38bdf8]">{ml.compass}</span>
      </div>

      {/* Glassmorphism panel */}
      <div className="absolute left-3 top-3 sm:left-5 sm:top-5 z-10 w-[calc(100%-1.5rem)] max-w-[320px] rounded-2xl border border-white/10 bg-slate-950/80 p-4 sm:p-5 shadow-2xl shadow-black/70 backdrop-blur-xl">
        <div className="mb-2 flex items-center gap-1.5 text-[11px] font-bold uppercase tracking-wider text-sky-400">
          {breadcrumb.split(" / ").map((part, i, arr) => (
            <span key={part} className={i === arr.length - 1 ? "text-sky-400 font-extrabold" : "text-slate-500"}>
              {part}
              {i < arr.length - 1 ? <span className="mx-1 text-slate-600">/</span> : null}
            </span>
          ))}
        </div>
        <h2 className="mb-1 text-base sm:text-lg font-black tracking-tight text-white">{title}</h2>
        <p className="mb-3 text-[11px] sm:text-xs leading-relaxed text-slate-400">{subtitle}</p>
        
        <div className="mb-3 rounded-xl border border-white/10 bg-white/[0.03] p-3 space-y-2">
          <div className="flex items-center justify-between text-xs">
            <span className="text-slate-400">{ml.areaLabel}:</span>
            <span className="font-bold text-slate-100">{statTarget}</span>
          </div>
          <div className="flex items-center justify-between text-xs">
            <span className="text-slate-400">{ml.popLabel}:</span>
            <span className="font-bold text-slate-100">{statPop}</span>
          </div>

          {/* Sonnendach Theme */}
          {(activeTopic === "solar" || activeTopic === "sonnendach") && (
            <div className="pt-2 border-t border-amber-500/20">
              <div className="mb-1.5 flex items-center justify-between text-[11px]">
                <span className="font-semibold text-amber-300">☀ BFE Sonnendach Potenzial</span>
              </div>
              <div className="flex items-center justify-between text-xs mb-1">
                <span className="text-slate-400">Mittlere Einstrahlung:</span>
                <span className="font-bold text-amber-400">{currentSolar.kwh} kWh/m²/Jahr</span>
              </div>
              <div className="flex items-center justify-between text-xs mb-1">
                <span className="text-slate-400">Eignungsklasse:</span>
                <span className="font-bold text-emerald-400">{currentSolar.rating}</span>
              </div>
              <div className="mt-2 h-1.5 w-full overflow-hidden rounded-full bg-amber-950/60">
                <div
                  className="h-full bg-gradient-to-r from-amber-400 to-yellow-300 rounded-full transition-all duration-300"
                  style={{ width: `${Math.min(100, Math.max(20, Math.round((currentSolar.kwh / 1450) * 100)))}%` }}
                />
              </div>
            </div>
          )}

          {/* Politik Theme */}
          {activeTopic === "politik" && (
            <div className="pt-2 border-t border-sky-500/20">
              <div className="mb-1 flex items-center justify-between text-[11px]">
                <span className="font-semibold text-sky-300">🗳 13. AHV-Rente (BFS)</span>
              </div>
              <div className="mb-1 flex justify-between text-[11px] font-bold">
                <span className="text-sky-400">{ml.voteYes}: {voteYes.toFixed(1)}%</span>
                <span className="text-rose-400">{ml.voteNo}: {noPct}%</span>
              </div>
              <div className="flex h-1.5 w-full overflow-hidden rounded-full bg-rose-950/80">
                <div className="h-full bg-gradient-to-r from-sky-400 to-blue-500 transition-all duration-300 rounded-full" style={{ width: `${voteYes}%` }} />
              </div>
            </div>
          )}

          {/* Planung Theme */}
          {activeTopic === "planung" && (
            <div className="pt-2 border-t border-indigo-500/20">
              <div className="mb-1.5 flex items-center justify-between text-[11px]">
                <span className="font-semibold text-indigo-300">🏗 Amtsblatt Baugesuche</span>
              </div>
              <div className="flex items-center justify-between text-xs mb-1">
                <span className="text-slate-400">Aktive Gesuche:</span>
                <span className="font-bold text-indigo-400">{baugesuche.length} im 20-Tage Fenster</span>
              </div>
              <div className="flex items-center justify-between text-xs">
                <span className="text-slate-400">Rechtsmittel:</span>
                <span className="font-bold text-emerald-400">Einsprachefrist läuft</span>
              </div>
            </div>
          )}

          {/* Ort Theme */}
          {activeTopic === "ort" && (
            <div className="pt-2 border-t border-emerald-500/20">
              <div className="mb-1.5 flex items-center justify-between text-[11px]">
                <span className="font-semibold text-emerald-300">📍 ARE ÖV & sonBASE Lärm</span>
              </div>
              <div className="flex items-center justify-between text-xs mb-1">
                <span className="text-slate-400">ÖV-Güteklasse:</span>
                <span className="font-bold text-emerald-400">Klasse {currentOev.cls}</span>
              </div>
              <div className="flex items-center justify-between text-xs mb-1">
                <span className="text-slate-400">Lärmbelastung Tag:</span>
                <span className="font-bold text-slate-200">{currentOev.noise} dB(A)</span>
              </div>
              <div className="flex items-center justify-between text-xs">
                <span className="text-slate-400">Steuerfuss:</span>
                <span className="font-bold text-sky-400">{currentTax}%</span>
              </div>
            </div>
          )}

          {/* ÖREB Theme */}
          {activeTopic === "oereb" && (
            <div className="pt-2 border-t border-blue-500/20">
              <div className="mb-1.5 flex items-center justify-between text-[11px]">
                <span className="font-semibold text-blue-300">⚖ ÖREB-Kataster (Swisstopo)</span>
              </div>
              <div className="flex items-center justify-between text-xs mb-1">
                <span className="text-slate-400">Zonierung:</span>
                <span className="font-bold text-blue-400">{currentOereb.zone}</span>
              </div>
              <div className="flex items-center justify-between text-xs">
                <span className="text-slate-400">Status:</span>
                <span className="font-bold text-emerald-400">Rechtskräftig</span>
              </div>
            </div>
          )}

          {/* Overview Theme */}
          {activeTopic === "overview" && (
            <div className="pt-2 border-t border-white/10">
              <div className="flex items-center justify-between text-xs mb-1">
                <span className="text-slate-400">Steuerfuss:</span>
                <span className="font-bold text-sky-400">{currentTax}%</span>
              </div>
              <div className="flex items-center justify-between text-xs mb-1">
                <span className="text-slate-400">ÖV-Klasse:</span>
                <span className="font-bold text-emerald-400">Klasse {currentOev.cls}</span>
              </div>
              <div className="flex items-center justify-between text-xs">
                <span className="text-slate-400">Solarertrag:</span>
                <span className="font-bold text-amber-400">{currentSolar.kwh} kWh/m²</span>
              </div>
            </div>
          )}
        </div>


        {showBack && (
          <button
            onClick={handleBack}
            className="w-full rounded-xl border border-sky-500/40 bg-sky-500/15 px-3 py-2 text-xs font-bold text-sky-300 transition-all hover:bg-sky-500/30 hover:text-white active:scale-95"
          >
            ← {ml.breadcrumb}
          </button>
        )}
      </div>

      <div
        ref={tooltipRef}
        data-testid="map-tooltip"
        className="pointer-events-none absolute z-20 -translate-x-1/2 -translate-y-[120%] rounded-xl border border-sky-400/40 bg-slate-950/90 px-3.5 py-2 text-xs font-medium text-slate-100 shadow-2xl shadow-black/80 backdrop-blur-md"
        style={{ display: "none" }}
      />

      <div className="pointer-events-none absolute bottom-3 left-1/2 z-10 -translate-x-1/2 rounded-full border border-white/10 bg-slate-950/70 px-4 py-1 text-[11px] font-medium tracking-wide text-slate-400 backdrop-blur-md shadow-md">
        {ml.hint}
      </div>
    </div>
  );
}

