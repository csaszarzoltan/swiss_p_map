// Stub: valós geokódolás Task 5-ben (Swisstopo search)
export const POSTCODE_COORDS: Record<string, [number, number]> = {
  "8001": [8.545, 47.377],
  "8004": [8.517, 47.392],
};

export function coordFor(postcode: string): [number, number] | undefined {
  return POSTCODE_COORDS[postcode];
}
