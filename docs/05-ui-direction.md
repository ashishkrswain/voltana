# UI/UX Direction

## 1. Aesthetic Brief

"Minimal, classic, with a hint of modernness." In practice:

- **Not** the typical neon-gradient, glassmorphism, EV-startup-pitch-deck look
  (avoid electric blue/green gradients, glowing icons, overly futuristic type).
- **Yes to:** generous whitespace, a restrained neutral palette (off-white/warm
  gray background, near-black text) with a single confident accent color,
  clean geometric sans-serif type, subtle borders instead of heavy shadows,
  understated iconography.
- Think: a well-designed travel/booking app (calm, trustworthy, information-
  dense but uncluttered) rather than a flashy consumer tech app.

## 2. Primary Screens

### Screen 1 — Vehicle Select
- Searchable dropdown/list: make → model → variant.
- Show key specs inline once selected (battery size, range, charge port type)
  so the user can confirm it's right before proceeding.

### Screen 2 — Route Input
- Origin / destination fields (autocomplete via maps API).
- Optional: adjust average speed assumption (default 60 km/h, slider or
  stepper), starting battery % (default 100%).
- Single clear primary action: "Plan Route."

### Screen 3 — Itinerary Result
- Map at top: route polyline, charger stop markers along it.
- Below: step-by-step list, one card per leg —
  - "Bangalore → Hassan charging stop"
  - Distance, duration, battery at arrival
  - Charger name/network, connector type, charge time needed
- Running summary bar: total distance, total time, number of stops.

### Screen 4 — Trip Detail / Stop Card (tap into a stop)
- Charger details: network, address, connector types, power rating.
- Note: "Live availability not yet supported — verify via [network]'s app
  before relying on this stop" (important honesty disclaimer for Phase 1,
  since you don't have live status yet).

## 3. Design System Basics

- **Typography:** one clean sans-serif (e.g. Inter, or a similar system font)
  — one weight for body, one heavier weight for headings/numbers (distances,
  times, battery %).
- **Color:** neutral base + one accent (e.g. a deep green or deep blue, evoking
  "electric" without being neon) + a clear status color for warnings (amber for
  "range tight," red for "no viable stop found").
- **Iconography:** simple line icons for battery, charger plug, clock, route —
  avoid overly literal "EV" cliché icons (lightning bolts everywhere).
- **Data density:** this is a planning tool people will actually read numbers
  from — don't sacrifice legibility of km/time/% figures for aesthetic
  minimalism. Numbers should be the most visually prominent element on each
  card.

## 4. Suggested Component List (for whichever frontend framework you use)

- VehicleSelector (searchable combobox)
- RouteInputForm
- MapView (route + charger markers)
- ItineraryStepCard (per-leg)
- TripSummaryBar (sticky top or bottom: total distance/time/stops)
- ChargerDetailSheet (modal/drawer for stop detail)
- RangeConfidenceBadge (small indicator showing whether range data is
  high/medium/low confidence for the selected vehicle — ties back to the
  `range_confidence` table in the schema doc)