import dynamic from "next/dynamic";

const Map = dynamic(() => import("./Map"), { ssr: false });

export default function Home() {
  return (
    <main className="mx-auto max-w-5xl p-6">
      <h1 className="text-2xl font-bold">Swiss P Map</h1>
      <p className="text-sm text-zinc-600">
        „A svájci környék egyetlen térképén” — Zürich pilot (ADR-001)
      </p>
      <div className="mt-4">
        <Map />
      </div>
      <p className="mt-3 text-xs text-zinc-500">
        Backend: <code>/api/v1/place/8004</code> · Swisstopo Light basemap
      </p>
    </main>
  );
}
