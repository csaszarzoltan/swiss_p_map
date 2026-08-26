export interface PlaceInfo {
  postcode: string;
  municipality: string;
  canton: string;
  steuerfuss_percent: number | null;
  noise_db_day: number | null;
  oev_class: string;
  gwr_building_count: number | null;
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
}

const BASE = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

async function getJson<T>(path: string): Promise<T> {
  const res = await fetch(`${BASE}${path}`);
  if (!res.ok) throw new Error(`API ${res.status}: ${path}`);
  return res.json() as Promise<T>;
}

export const api = {
  place: (postcode: string) => getJson<PlaceInfo>(`/api/v1/place/${postcode}`),
  politics: (postcode: string) =>
    getJson<DistrictRepresentatives>(`/api/v1/politics/representatives?postcode=${postcode}`),
  planning: (postcode?: string, activeOnly = true) =>
    getJson<{ items: Baugesuch[] }>(
      `/api/v1/planning/baugesuche?${new URLSearchParams({
        ...(postcode ? { postcode } : {}),
        active_only: String(activeOnly),
      }).toString()}`,
    ),
};
