"use client";

import { useEffect, useRef, useState } from "react";
import * as THREE from "three";
import { OrbitControls } from "three/addons/controls/OrbitControls.js";
import gsap from "gsap";
import { SWISS_CANTONS } from "./swissCantons";

// A svájc_3d_terkep.html logikájának vanilla→React portja — ADR-003

const INITIAL_CAM = { x: 0, y: 9.5, z: 16.5 };
const INITIAL_TARGET = { x: 0, y: 0, z: -0.2 };

const BASE_GLASS = { color: 0x1e293b, opacity: 0.42 };
const BASE_EDGE = 0x64748b;
const HOVER_EMISSIVE = 0x0284c7;

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
    opacity: isCity ? 0.6 : BASE_GLASS.opacity,
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
    baseY: isCity ? 0.4 : 0,
    edgeLines,
    isCity,
    origColor: BASE_GLASS.color,
    origOpacity: isCity ? 0.6 : BASE_GLASS.opacity,
  };
  if (isCity) mesh.position.y = 0.4;
  return mesh;
}

export default function Map3D() {
  const containerRef = useRef<HTMLDivElement>(null);
  const tooltipRef = useRef<HTMLDivElement>(null);
  const [breadcrumb, setBreadcrumb] = useState("SVÁJC");
  const [title, setTitle] = useState("Svájci Államszövetség");
  const [subtitle, setSubtitle] = useState(
    "Vidd az egeret egy kanton fölé a 3D kiemeléshez, majd kattints a kantonon belüli városok felfedezéséhez!",
  );
  const [statTarget, setStatTarget] = useState("26 Kanton");
  const [statPop, setStatPop] = useState("8.9 Millió");
  const [voteYes, setVoteYes] = useState(61.4);
  const [showBack, setShowBack] = useState(false);
  const stateRef = useRef<{
    selectedCanton: THREE.Mesh | null;
    selectedCity: THREE.Mesh | null;
    currentHovered: THREE.Mesh | null;
    mainGroup: THREE.Group | null;
    subGroup: THREE.Group | null;
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
    camera: null,
    controls: null,
    raycaster: new THREE.Raycaster(),
    mouse: new THREE.Vector2(),
  });

  // Tooltip imperative — ne triggereljen re-rendert egérmozgásra
  const tip = (d: { name: string; pop: string; yes: number } | null, x?: number, y?: number) => {
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
    el.innerHTML = `<strong>${d.name}</strong>Népesség: ${d.pop}<br/>Támogatottság: <span style="color:#38bdf8;font-weight:700;">${d.yes}% IGEN</span>`;
  };

  const applyHover = (mesh: THREE.Mesh) => {
    document.body.style.cursor = "pointer";
    gsap.to(mesh.position, { y: (mesh.userData.baseY as number) + 0.65, duration: 0.28, ease: "power2.out" });
    gsap.to((mesh.material as THREE.MeshStandardMaterial).color, { r: 0.22, g: 0.74, b: 0.97, duration: 0.2 });
    gsap.to(mesh.material as THREE.MeshStandardMaterial, { opacity: 0.82, duration: 0.2 });
    (mesh.material as THREE.MeshStandardMaterial).emissive.setHex(HOVER_EMISSIVE);
    (mesh.material as THREE.MeshStandardMaterial).emissiveIntensity = 0.45;
    const _el1 = (mesh.userData.edgeLines as THREE.LineSegments).material as THREE.LineBasicMaterial;
    _el1.color.setHex(0xe0f2fe);
    _el1.opacity = 0.95;
    tip(mesh.userData as { name: string; pop: string; yes: number });
    // panel stats
    const d = mesh.userData as { name: string; pop: string; yes: number };
    setStatTarget(d.name);
    setStatPop(d.pop);
    setVoteYes(d.yes);
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
      const box = new THREE.Box3().setFromObject(s.selectedCanton!);
      const center = new THREE.Vector3();
      box.getCenter(center);
      gsap.to(s.camera!.position, { x: center.x, y: center.y + 4.2, z: center.z + 7.2, duration: 1.0, ease: "power2.inOut" });
      gsap.to(s.controls!.target, { x: center.x, y: center.y, z: center.z, duration: 1.0, ease: "power2.inOut" });
      s.subGroup!.children.forEach((cm) => {
        gsap.to((cm as THREE.Mesh).material as THREE.MeshStandardMaterial, { opacity: 0.6, duration: 0.4 });
      });
      setBreadcrumb(`SVÁJC / ${(s.selectedCanton!.userData as { name: string }).name.toUpperCase()}`);
      setTitle(`${(s.selectedCanton!.userData as { name: string }).name} kanton`);
      setSubtitle("Körzeti adatok megnyitva. Vidd az egeret a városok fölé a kiemeléshez!");
      const d = s.selectedCanton!.userData as { name: string; pop: string; yes: number };
      setStatTarget(d.name);
      setStatPop(d.pop);
      setVoteYes(d.yes);
    } else if (s.selectedCanton) {
      s.selectedCanton = null;
      s.subGroup!.clear();
      gsap.to(s.camera!.position, { x: INITIAL_CAM.x, y: INITIAL_CAM.y, z: INITIAL_CAM.z, duration: 1.2, ease: "power2.inOut" });
      gsap.to(s.controls!.target, { x: INITIAL_TARGET.x, y: INITIAL_TARGET.y, z: INITIAL_TARGET.z, duration: 1.2, ease: "power2.inOut" });
      s.mainGroup!.children.forEach((c) => {
        gsap.to(c.position, { y: 0, duration: 0.6 });
        gsap.to((c as THREE.Mesh).material as THREE.MeshStandardMaterial, { opacity: 0.42, duration: 0.6 });
      });
      setBreadcrumb("SVÁJC");
      setTitle("Svájci Államszövetség");
      setSubtitle("Vidd az egeret egy kanton fölé a 3D kiemeléshez, majd kattints a kantonon belüli városok felfedezéséhez!");
      setStatTarget("26 Kanton");
      setStatPop("8.9 Millió");
      setVoteYes(61.4);
      setShowBack(false);
    }
  };

  useEffect(() => {
    const container = containerRef.current;
    if (!container) return;

    const scene = new THREE.Scene();
    scene.fog = new THREE.FogExp2(0x030712, 0.025);
    const camera = new THREE.PerspectiveCamera(42, container.clientWidth / container.clientHeight, 0.1, 1000);
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

    scene.add(new THREE.AmbientLight(0xffffff, 0.65));
    const dl1 = new THREE.DirectionalLight(0xffffff, 0.9);
    dl1.position.set(10, 20, 15);
    dl1.castShadow = true;
    scene.add(dl1);
    const dl2 = new THREE.DirectionalLight(0x38bdf8, 0.4);
    dl2.position.set(-15, 10, -10);
    scene.add(dl2);
    const grid = new THREE.GridHelper(36, 36, 0x1e293b, 0x0f172a);
    grid.position.y = -0.05;
    scene.add(grid);

    const mainGroup = new THREE.Group();
    const subGroup = new THREE.Group();
    scene.add(mainGroup);
    scene.add(subGroup);
    stateRef.current.mainGroup = mainGroup;
    stateRef.current.subGroup = subGroup;
    stateRef.current.camera = camera;
    stateRef.current.controls = controls;

    SWISS_CANTONS.forEach((canton) => {
      const mesh = buildMesh(canton.points as [number, number][], 0.35, canton as unknown as Record<string, unknown>, false);
      mainGroup.add(mesh);
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
      if (!s.currentHovered) return;
      const data = s.currentHovered.userData as { isCity?: boolean; cities?: { points: [number, number][]; name: string; pop: string; yes: number; id: string }[]; name: string };
      if (!s.selectedCanton && !data.isCity) {
        s.selectedCanton = s.currentHovered;
        const box = new THREE.Box3().setFromObject(s.selectedCanton);
        const center = new THREE.Vector3();
        box.getCenter(center);
        gsap.to(camera.position, { x: center.x, y: center.y + 4.2, z: center.z + 7.2, duration: 1.3, ease: "power3.inOut" });
        gsap.to(controls.target, { x: center.x, y: center.y, z: center.z, duration: 1.3, ease: "power3.inOut" });
        mainGroup.children.forEach((c) => {
          if (c !== s.selectedCanton) {
            gsap.to(c.position, { y: -0.6, duration: 0.5 });
            gsap.to((c as THREE.Mesh).material as THREE.MeshStandardMaterial, { opacity: 0.08, duration: 0.5 });
          }
        });
        subGroup.clear();
        if (data.cities?.length) {
          data.cities.forEach((city) => {
            const m = buildMesh(city.points, 0.45, city as unknown as Record<string, unknown>, true);
            subGroup.add(m);
          });
        }
        setBreadcrumb(`SVÁJC / ${data.name.toUpperCase()}`);
        setTitle(`${data.name} kanton`);
        setSubtitle("Körzeti adatok megnyitva. Vidd az egeret egy város/körzet fölé, vagy kattints rá a részletekhez!");
        setShowBack(true);
        return;
      }
      if (s.selectedCanton && data.isCity && !s.selectedCity) {
        s.selectedCity = s.currentHovered;
        const box = new THREE.Box3().setFromObject(s.selectedCity);
        const center = new THREE.Vector3();
        box.getCenter(center);
        gsap.to(camera.position, { x: center.x, y: center.y + 2.5, z: center.z + 4.0, duration: 1.1, ease: "power3.inOut" });
        gsap.to(controls.target, { x: center.x, y: center.y, z: center.z, duration: 1.1, ease: "power3.inOut" });
        subGroup.children.forEach((cm) => {
          if (cm !== s.selectedCity) gsap.to((cm as THREE.Mesh).material as THREE.MeshStandardMaterial, { opacity: 0.1, duration: 0.4 });
        });
        setBreadcrumb(`SVÁJC / ${(s.selectedCanton.userData as { name: string }).name.toUpperCase()} / ${data.name.toUpperCase()}`);
        setTitle(data.name);
        setSubtitle("Települési szintű szavazóköri végeredmény.");
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

  const noPct = (100 - voteYes).toFixed(1);

  return (
    <div className="relative w-full overflow-hidden rounded-xl border border-white/10" style={{ height: "62vh", minHeight: 380, background: "radial-gradient(circle at 50% 30%, #111827 0%, #030712 100%)" }} data-testid="map-3d">
      <div ref={containerRef} className="absolute inset-0" data-testid="map-3d-canvas" />

      {/* Iránytű */}
      <div className="pointer-events-none absolute right-4 top-4 z-10 flex h-12 w-12 flex-col items-center justify-center rounded-full border border-white/10 bg-[rgba(17,24,39,0.7)] shadow-[0_4px_20px_rgba(0,0,0,0.4)] backdrop-blur-[12px]">
        <div className="mb-0.5 h-0 w-0 border-x-[5px] border-b-[9px] border-x-transparent border-b-[#38bdf8]" />
        <span className="text-[11px] font-bold text-[#38bdf8]">É</span>
      </div>

      {/* Glassmorphism panel */}
      <div className="absolute left-4 top-4 z-10 w-[320px] rounded-[14px] border border-white/10 bg-[rgba(15,23,42,0.75)] p-[22px] shadow-[0_20px_40px_rgba(0,0,0,0.6)] backdrop-blur-[16px]">
        <div className="mb-2 flex items-center gap-1.5 text-[11px] font-bold uppercase tracking-[1px] text-[#38bdf8]">
          {breadcrumb.split(" / ").map((part, i, arr) => (
            <span key={part} className={i === arr.length - 1 ? "text-[#38bdf8]" : "text-slate-500"}>
              {part}
              {i < arr.length - 1 ? <span className="mx-1 text-slate-500">/</span> : null}
            </span>
          ))}
        </div>
        <h2 className="mb-1.5 text-[20px] font-bold tracking-[-0.3px] text-white">{title}</h2>
        <p className="mb-4 text-[12px] leading-[1.4] text-slate-400">{subtitle}</p>
        <div className="mb-3 rounded-lg border border-white/5 bg-white/[0.04] p-3">
          <div className="mb-2 flex items-center justify-between text-[13px]">
            <span className="text-slate-400">Terület / Egység:</span>
            <span className="font-semibold text-slate-100">{statTarget}</span>
          </div>
          <div className="mb-2 flex items-center justify-between text-[13px]">
            <span className="text-slate-400">Népesség:</span>
            <span className="font-semibold text-slate-100">{statPop}</span>
          </div>
          <div className="mt-2">
            <div className="mb-1 flex justify-between text-[11px] font-semibold">
              <span className="text-[#38bdf8]">IGEN: {voteYes.toFixed(1)}%</span>
              <span className="text-[#f87171]">NEM: {noPct}%</span>
            </div>
            <div className="flex h-1.5 w-full overflow-hidden rounded bg-[rgba(239,68,68,0.5)]">
              <div className="h-full bg-[#38bdf8] transition-[width] duration-300" style={{ width: `${voteYes}%` }} />
            </div>
          </div>
        </div>
        {showBack && (
          <button
            onClick={handleBack}
            className="w-full rounded-lg border border-[#38bdf8]/40 bg-[#38bdf8]/15 px-3 py-2.5 text-[13px] font-semibold text-[#38bdf8] transition hover:bg-[#38bdf8]/30 hover:text-white"
          >
            ← Vissza az előző nézethez
          </button>
        )}
      </div>

      <div
        ref={tooltipRef}
        data-testid="map-tooltip"
        className="pointer-events-none absolute z-20 -translate-x-1/2 -translate-y-[120%] rounded-md border border-[#38bdf8]/30 bg-[rgba(15,23,42,0.88)] px-3 py-2 text-xs shadow-[0_8px_24px_rgba(0,0,0,0.5)] backdrop-blur-[8px]"
        style={{ display: "none" }}
      />

      <div className="pointer-events-none absolute bottom-3 left-1/2 z-10 -translate-x-1/2 rounded-full border border-white/5 bg-[rgba(15,23,42,0.6)] px-4 py-1.5 text-xs tracking-[0.5px] text-slate-500 backdrop-blur-[8px]">
        Bal gomb: Forgatás · Jobb gomb: Eltolás · Görgő: Zoom
      </div>
    </div>
  );
}
