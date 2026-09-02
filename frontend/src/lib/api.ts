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


export interface PropertySegment {
  segment: "single_family_house" | "condominium";
  average_price_chf_m2: number;
  quarterly_index: number;
  change_1y_percent: number;
  change_5y_percent: number;
}
export interface PropertyPriceAssessment { canton: string; postcode: string; reference_period: string; source: string; quality_state: string; segments: PropertySegment[]; }
export interface TaxEntry { canton: string; steuerfuss_percent: number; national_rank: number; band: "low" | "medium" | "high"; }
export interface TaxComparison { canton: string; national_average_percent: number; selected: TaxEntry; ranking: TaxEntry[]; neighboring_cantons: TaxEntry[]; source: string; }
export interface HazardAssessment { postcode: string; risk_level: "none" | "low" | "medium" | "high"; hazards: Array<{ hazard_type: string; risk_level: string }>; source: string; disclaimer: string; }
export interface IsosAssessment { postcode: string; protected: boolean; classification: "ISOS I" | "ISOS II" | null; site_name: string | null; delay_risk: "low" | "medium" | "high"; source: string; }

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

export interface DistrictComparison { postcode: string; municipality: string; steuerfuss_percent: number; price_chf_m2: number; noise_db_day: number; oev_class: string; school_count: number; solar_kwh_m2: number; }
export interface MobilityAssessment { postcode: string; nearest_station: string; service_interval_min: number; intercity_connection: boolean; hubs: Array<{hub:string;minutes:number;zone:number}>; source: string; }
export interface ParcelAssessment { postcode: string; parcel_nr: string; area_m2: number; zoning: string; source: string; official_url: string; trust_state: "cadastral_registry"; }

export const api = {
  districtComparison: (codes: string[]) => getJson<{items: DistrictComparison[]}>(`/api/v1/districts/compare?postcodes=${codes.join(",")}`),
  mobility: (postcode: string) => getJson<MobilityAssessment>(`/api/v1/mobility/isochrones?postcode=${postcode}`),
  parcel: (postcode: string, parcelNr: string) => getJson<ParcelAssessment>(`/api/v1/cadastre/parcel?postcode=${postcode}&parcel_nr=${encodeURIComponent(parcelNr)}`),
  provenance: () => getJson<{items: Array<{id:string;source:string;trust_state:string;refreshed_at:string}>}>(`/api/v1/system/sources-provenance`),
  place: (postcode: string, live = true) =>
    getJson<PlaceInfo>(`/api/v1/place/${postcode}${live ? "?live=true" : ""}`),
  politics: (postcode: string, live = true) =>
    getJson<DistrictRepresentatives>(`/api/v1/politics/representatives?postcode=${postcode}${live ? "&live=true" : ""}`),
  propertyPrices: (canton: string, postcode: string) => getJson<PropertyPriceAssessment>(`/api/v1/property/prices?canton=${canton}&postcode=${postcode}`),
  taxComparison: (canton: string) => getJson<TaxComparison>(`/api/v1/tax/comparison?canton=${canton}`),
  hazardAssessment: (postcode: string, lat: number, lon: number) => getJson<HazardAssessment>(`/api/v1/hazard/assessment?postcode=${postcode}&lat=${lat}&lon=${lon}`),
  isosAssessment: (postcode: string) => getJson<IsosAssessment>(`/api/v1/heritage/isos?postcode=${postcode}`),
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
