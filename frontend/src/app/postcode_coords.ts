// Fallback stub (offline esetre)
export const POSTCODE_COORDS: Record<string, [number, number]> = {
  "8001": [8.545, 47.377],
  "8004": [8.517, 47.392],
};

export function coordFor(postcode: string): [number, number] | undefined {
  return POSTCODE_COORDS[postcode];
}

export async function resolvePostcode(postcode: string): Promise<[number, number]> {
  // audit A: már nem csak PLZ, de a compat kedvéért postcode néven fut
  try {
    const res = await fetch(
      `https://api3.geo.admin.ch/rest/services/api/SearchServer?searchText=${encodeURIComponent(postcode)}&type=locations&limit=1`,
    );
    const json = (await res.json()) as {
      results?: Array<{ attrs: { lon: number; lat: number } }>;
    };
    const attrs = json.results?.[0]?.attrs;
    if (attrs && typeof attrs.lon === "number" && typeof attrs.lat === "number") {
      return [attrs.lon, attrs.lat];
    }
  } catch {
    // network/CORS offline → fallback
  }
  return POSTCODE_COORDS[postcode] ?? [8.54, 47.378];
}

export async function resolveQuery(query: string): Promise<[number, number] | null> {
  // audit A: szabad szöveg (cím/község/PLZ) — Swisstopo type=locations a teljes címre is jó
  const q = query.trim();
  if (!q) return null;
  if (/^\d{4}$/.test(q)) return resolvePostcode(q);
  try {
    const res = await fetch(
      `https://api3.geo.admin.ch/rest/services/api/SearchServer?searchText=${encodeURIComponent(q)}&type=locations&limit=1`,
    );
    const json = (await res.json()) as {
      results?: Array<{ attrs: { lon: number; lat: number } }>;
    };
    const attrs = json.results?.[0]?.attrs;
    if (attrs && typeof attrs.lon === "number" && typeof attrs.lat === "number") {
      return [attrs.lon, attrs.lat];
    }
  } catch {
    // fallback → null (nem ugrik a térkép)
  }
  return null;
}
