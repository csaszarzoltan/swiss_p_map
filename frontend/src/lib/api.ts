export interface PlaceInfo {
  postcode: string;
  municipality: string;
  canton: string;
  steuerfuss_percent: number | null;
  noise_db_day: number | null;
  oev_class: string;
  gwr_building_count: number | null;
  solar_kwh_m2: number | null;
  solar_class: string | null;
  oereb_zone: string | null;
  steuerfuss_source: string;
}

export interface Representative {
  id: string;
  name: string;
  party: string;
  wahlkreis: string;
}

export interface DistrictRepresentatives {
  district_name: string;
  postcode: string;
  representatives: Representative[];
}

export interface Baugesuch {
  id: string;
  title: string;
  municipality: string;
  municipality_id: number | null;
  postcode: string;
  canton: string;
  publication_date: string;
  expiration_date: string;
  auflage_start: string;
  auflage_end: string;
  source_url: string;
  geocode_precision: string;
  lat: number | null;
  lon: number | null;
}

const BASE = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

async function getJson<T>(path: string): Promise<T> {
  const res = await fetch(`${BASE}${path}`);
  if (!res.ok) throw new Error(`API ${res.status}: ${path}`);
  return res.json() as Promise<T>;
}

export const api = {
  place: (postcode: string, live = true) =>
    getJson<PlaceInfo>(`/api/v1/place/${postcode}${live ? "?live=true" : ""}`),
  politics: (postcode: string, live = true) =>
    getJson<DistrictRepresentatives>(`/api/v1/politics/representatives?postcode=${postcode}${live ? "&live=true" : ""}`),
  planning: (postcode?: string, activeOnly = true) =>
    getJson<{ items: Baugesuch[] }>(
      `/api/v1/planning/baugesuche?${new URLSearchParams({
        ...(postcode ? { postcode } : {}),
        active_only: String(activeOnly),
      }).toString()}`,
    ),
};
