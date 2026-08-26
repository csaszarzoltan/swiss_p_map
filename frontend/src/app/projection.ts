/** Lon/lat → Map3D model X/Y (same projection as swissCantons/mapOverlay gen). */
const COS_LAT = Math.cos((46.8 * Math.PI) / 180);
const MIN_LON = 5.956800664952974;
const MAX_LON = 10.493446773955753;
const MIN_LAT = 45.81913730594624;
const MAX_LAT = 47.80743900893902;
const RAW_W = (MAX_LON - MIN_LON) * COS_LAT;
const RAW_H = MAX_LAT - MIN_LAT;
const SCALE_ZOOM = Math.min(9.5 / RAW_W, 6.2 / RAW_H);
const CX = ((MIN_LON + MAX_LON) / 2) * COS_LAT;
const CY = (MIN_LAT + MAX_LAT) / 2;

export function lonLatToModel(lon: number, lat: number): [number, number] {
  return [(lon * COS_LAT - CX) * SCALE_ZOOM, (lat - CY) * SCALE_ZOOM];
}
