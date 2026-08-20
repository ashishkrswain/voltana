# Getting Started — Suggested Build Order

Given your background (Python, FastAPI, LangGraph/LangChain, React/Node
familiarity), here's a pragmatic solo build order that gets you a demoable
product fastest.

## Suggested Stack

- **Backend:** Python + FastAPI (matches your production experience)
  - Vehicle DB, charger DB, route-planning endpoint as REST APIs
- **Database:** PostgreSQL (relational fits the vehicle/charger schema well;
  PostGIS extension if you want proper geospatial queries for "chargers near
  this route" later — can start without it using simple bounding-box math)
- **Frontend:** React (or Next.js if you want SSR/easy deployment) + a mapping
  library (Google Maps JS SDK or Mapbox GL JS, matching whichever routing API
  you pick)
- **Hosting (MVP):** Railway/Render/Fly.io for backend+DB, Vercel for frontend
  — all have generous free/cheap tiers for a solo pre-revenue build

## Build Order

1. **Vehicle database** — stand up the Postgres schema from
   `02-vehicle-database-schema.md`, seed with top 30–40 models (CSV → script →
   DB). This alone is a useful, shippable artifact (e.g. a simple "compare EVs"
   page) even before the route planner exists.
2. **Charger database (seeded)** — manually seed 1–2 corridors
   (Bangalore–Goa first, since that's your own use case) from public station
   listings.
3. **Routing integration** — get Google Maps Directions API working for a
   basic origin→destination polyline + distance/duration.
4. **Range/stop calculation engine** — implement the pipeline in
   `04-route-engine-design.md` as a pure function/service first (testable
   without any UI).
5. **Minimal frontend** — Vehicle Select → Route Input → Itinerary Result, per
   `05-ui-direction.md`. Doesn't need to be pretty yet — get the flow working
   end to end.
6. **Polish UI** to the minimal/classic/modern direction once the core flow
   is validated.
7. **Expand vehicle + charger data coverage** once the core product works for
   your first corridor.

## File Structure Suggestion

```
ev-planner/
├── backend/
│   ├── app/
│   │   ├── models/          # SQLAlchemy models (vehicles, chargers, efficiency_curve)
│   │   ├── routers/         # FastAPI route handlers
│   │   ├── services/
│   │   │   ├── routing.py       # Google Maps API wrapper
│   │   │   └── trip_planner.py  # the greedy stop-selection engine
│   │   └── main.py
│   ├── data/
│   │   ├── vehicles_seed.csv
│   │   └── chargers_seed.csv
│   └── scripts/
│       └── seed_db.py
├── frontend/
│   └── (React/Next.js app)
└── docs/                    # this PRD + design docs live here
```

## First Milestone to Aim For

A working local demo: select a Tata Nexon EV or Ola S1 Pro, enter Bangalore →
Goa, and get back a real itinerary with 2–3 charging stops, distances, and
estimated times — using seeded (not live) charger data. That's a legitimate
MVP you could show to a potential co-founder, early user, or investor.