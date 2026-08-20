# Voltana

Plan intercity EV trips across India with vehicle-specific range modeling and
cross-network charger discovery.

## What it does

Enter your EV, origin, and destination — Voltana gives you a complete drivable
itinerary: which chargers to stop at, at what kilometer mark, how long to charge,
and total trip time. Works across Tata Power, Statiq, ChargeZone, Ather Grid,
Jio-BP, and other networks in a single view.

## Why it exists

Indian EV drivers today juggle 3-5 different charging network apps to plan one
trip, manually guess charger locations along their route, and mentally estimate
range without accounting for their vehicle, speed, or terrain. Voltana replaces
that entire process with one tool.

## Phase 1 (current)

- Structured database of every EV sold in India (2W/3W/4W) with real-world range specs
- Route planning with vehicle-specific range and charge-stop calculations
- Cross-network charger location data overlaid on routes
- Clean, minimal web UI

## Tech Stack

- **Backend:** Python, FastAPI, PostgreSQL
- **Frontend:** React / Next.js
- **Maps:** Google Maps Directions API
- **Hosting:** TBD (Railway/Render/Vercel)

## Project Status

Early development. Building the core route planning engine and vehicle database.

## License

TBD