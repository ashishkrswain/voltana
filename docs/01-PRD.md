# PRD — Unified India EV Route & Charging Planner

**Status:** Draft v1
**Owner:** Ashish (solo founder)
**Last updated:** 2026-08-20

---

## 1. Problem Statement

EV drivers in India cannot plan a multi-city trip in one place. To go from Bangalore
to Goa, a driver today must:

- Check 3–5 different charging network apps (Tata Power EZ, Statiq, ChargeZone,
  Ather Grid, Jio-BP Pulse, etc.) because no single network covers a whole route.
- Manually guess which chargers fall along their path, since none of these apps do
  route-based planning across networks.
- Manually estimate range remaining, based on rough vehicle knowledge, with no tool
  accounting for their specific vehicle model, speed, or terrain.
- Arrive at a charger with no confidence it is functional, unoccupied, or even still
  operational.

There is no single tool in India that combines **route planning + vehicle-specific
range modeling + cross-network charger discovery** into one experience.

## 2. Vision

One app where an Indian EV owner enters origin, destination, and vehicle, and gets
back a complete, drivable itinerary: which chargers to stop at, at what kilometer
mark, how long to charge, and total trip time — regardless of which network operates
that charger.

## 3. Goals (Phase 1 — what we're building right now)

1. A structured, comprehensive database of every EV (2W/3W/4W) sold in India, with
   range and performance specs.
2. A road/route mapping layer for India (leveraging an existing maps/routing
   provider, not building maps from scratch).
3. A route planner: user selects vehicle + origin + destination → app returns a
   distance/time/charge-stop breakdown.
4. Charger location data overlaid on the route (static/known locations first —
   live status is Phase 2).
5. A clean, minimal, modern UI — not cluttered, not neon-tech-bro, more "classic
   with a hint of modern."

## 4. Non-Goals (explicitly out of scope for Phase 1)

- Live/real-time charger occupancy or functionality status (requires per-network
  API or OCPI integration — Phase 2+).
- Payments or in-app charging session initiation.
- Booking/reservation of a charging slot.
- Community reviews/check-ins (PlugShare-style) — maybe Phase 3.
- iOS/Android native apps — start as a responsive web app.

## 5. Target User

Indian EV owner (2W, 3W, or 4W) planning an intercity trip who currently has to use
multiple apps and mentally calculate range/charging stops themselves.

## 6. Core User Flow

1. User opens app, selects their vehicle from a searchable list (make + model +
   variant + battery size).
2. User enters origin and destination (or picks on map).
3. App calculates:
   - Total route distance and estimated drive time at a given average speed.
   - Vehicle's real-world range at that speed, adjusted for known efficiency
     data.
   - Number of charging stops required, and *where* along the route (km marker)
     they should happen based on remaining range and charger locations.
   - Estimated charge time needed at each stop (based on charger power rating vs.
     vehicle's max charge rate).
   - Running total: elapsed distance, elapsed time, battery % at each leg.
4. App displays this as a step-by-step itinerary + a map with markers.
5. User can adjust average speed assumption and see the plan recalculate.

## 7. Key Features — Phase 1 Detail

### 7.1 Vehicle Database
- Every EV (2W scooters/motorcycles, 3W autos, 4W cars) sold in India.
- Fields: make, model, variant, battery capacity (kWh), ARAI-certified range,
  real-world estimated range, top speed, charging port type(s) (AC/DC, connector
  standard), max AC charge rate (kW), max DC charge rate (kW), 0–80% DC charge
  time, efficiency (Wh/km) at different speed bands if available.
- See `02-vehicle-database-schema.md` and `03-data-sourcing-strategy.md`.

### 7.2 Route Planning Engine
- Given origin, destination, and vehicle: compute route via a mapping API
  (Google Maps Directions / Mapbox / OpenStreetMap + OSRM).
- Overlay known charger locations near the route corridor (within some buffer,
  e.g. 2–5 km of the route line).
- Range-aware stop planner: a simple greedy/graph algorithm that picks charging
  stops such that the vehicle never runs below a safety buffer (e.g. 15–20%
  battery) before the next stop.
- See `04-route-engine-design.md`.

### 7.3 Charger Data Layer (static, Phase 1)
- Aggregate publicly available charger location datasets (Tata Power, Statiq,
  ChargeZone, Jio-BP, PlugShare-listed stations, OCPI feeds where available).
- Store: name, network/operator, lat/lng, connector types available, power
  rating (kW) per connector, address.
- No live status in Phase 1 — status field defaults to "unknown," clearly
  labeled in UI so users aren't misled.

### 7.4 UI/UX Direction
- Minimal, classic-with-modern-touches: whitespace-forward, restrained color
  palette (1 accent color + neutrals), no gradient/neon "tech startup" clichés.
- Primary screens: Vehicle Select → Route Input → Itinerary Result (map + step
  list) → Trip Detail (per-stop card).
- See `05-ui-direction.md`.

## 8. Success Metrics (Phase 1, pre-launch/solo build)

- Vehicle database covers ≥ 95% of EVs currently on sale in India across 2W/3W/4W.
- Route planner produces a correct, drivable itinerary for 10 test routes across
  varying distances (short intracity to long intercity like Bangalore–Goa).
- A test user (non-technical) can plan a trip end-to-end without confusion.

## 9. Phased Roadmap (high-level)

- **Phase 1 (now):** Vehicle DB + route planner + static charger map. Solo build.
- **Phase 2:** Live charger status — via OCPI integration (piggyback on existing
  open infrastructure like One Bharat Charge) and/or direct network partnerships.
- **Phase 3:** Community check-ins/reviews, booking, payments, native apps.

## 10. Open Questions

- Which mapping/routing provider — Google Maps (best India coverage, cost at
  scale) vs Mapbox vs self-hosted OSRM on OpenStreetMap (free, more setup)?
- Vehicle DB — manual curation vs scraping manufacturer sites vs a hybrid with
  community submission for corrections?
- How to source charger location data at all without live APIs — see
  `03-data-sourcing-strategy.md` for options and legal/ToS considerations.