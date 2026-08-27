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
  risk_level?: "low" | "medium" | "high" | null;
  risk_reason?: string | null;
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
  contractor?: string | null;
  architect?: string | null;
  parcel_number?: string | null;
  zone_type?: string | null;
  risk_level?: "low" | "medium" | "high" | null;
  distance_m?: number | null;
}

export interface VoteProposalOverview {
  proposal_id: number;
  date: string;
  titles: Record<string, string>;
  national_yes_percent: number;
  national_no_percent: number;
  national_turnout_percent: number;
}

const BASE = process.env.NEXT_PUBLIC_API_URL ?? "http://127.0.0.1:8310";

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

export async function fetchPlace(postcode: string, live = false): Promise<PlaceInfo | null> {
  const url = `${BASE}/api/v1/place/${postcode}${live ? "?live=true" : ""}`;
  const res = await fetch(url);
  if (!res.ok) return null;
  return res.json() as Promise<PlaceInfo>;
}

export async function fetchPolitics(postcode: string, live = false): Promise<DistrictRepresentatives | null> {
  const url = `${BASE}/api/v1/politics/representatives?postcode=${postcode}${live ? "&live=true" : ""}`;
  const res = await fetch(url);
  if (!res.ok) return null;
  return res.json() as Promise<DistrictRepresentatives>;
}

export async function fetchBaugesuche(postcode: string): Promise<Baugesuch[]> {
  const res = await fetch(`${BASE}/api/v1/planning/baugesuche?postcode=${postcode}&active_only=false`);
  if (!res.ok) return [];
  const data = (await res.json()) as { items?: Baugesuch[] };
  return data.items ?? [];
}

export async function fetchVoteProposals(): Promise<VoteProposalOverview[]> {
  const res = await fetch(`${BASE}/api/v1/politics/votes/list`);
  if (!res.ok) return [];
  const data = (await res.json()) as { items?: VoteProposalOverview[] };
  return data.items ?? [];
}

export async function fetchVoteProposal(id: number): Promise<unknown | null> {
  const res = await fetch(`${BASE}/api/v1/politics/votes/${id}`);
  if (!res.ok) return null;
  return res.json();
}
