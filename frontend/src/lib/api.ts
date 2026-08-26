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
};
