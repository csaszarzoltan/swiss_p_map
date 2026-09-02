"use client";

import CostOfLivingCalculator from "./civic/CostOfLivingCalculator";
import VotingVisualCard from "./civic/VotingVisualCard";
import WasteCalendarVisual from "./civic/WasteCalendarVisual";
import WeatherVisualWidget from "./civic/WeatherVisualWidget";

export default function ResidentCivicPanels({ postcode }: { postcode: string }) {
  return (
    <section aria-label="Civic intelligence" className="mt-4 grid gap-3 md:grid-cols-2 xl:grid-cols-4">
      <VotingVisualCard />
      <WeatherVisualWidget />
      <WasteCalendarVisual />
      <CostOfLivingCalculator postcode={postcode} />
    </section>
  );
}
