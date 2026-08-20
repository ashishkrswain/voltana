# Data Sourcing Strategy

## 1. Vehicle Specs

**Sources, in order of trust:**

1. **Manufacturer official spec sheets / press kits** — battery capacity, ARAI
   range, top speed, charge port type, charge times. Usually accurate but the
   "range" figure is ARAI/marketing, not real-world.
2. **ARAI certification database** — where publicly accessible, cross-check
   official certified range.
3. **Enthusiast/review publications** (Autocar India, Team-BHP, Electric Vehicle
   Web, etc.) — often publish real-world range test results after driving the
   vehicle in mixed conditions. This is your best source for
   `real_world_range_km`.
4. **Community-submitted data** (Phase 1.5+) — once you have users, let them
   submit their own observed range/efficiency, similar to how PlugShare
   crowdsources charger reliability. Weight this against manufacturer data
   rather than trusting either blindly.

**Practical approach for solo build:**
- Start with a manually curated spreadsheet/CSV covering the top 30–40
  best-selling EV models (this covers the large majority of vehicles on Indian
  roads — Tata, MG, Mahindra, Hyundai for 4W; Ola, Ather, TVS, Bajaj for 2W).
- Expand to long-tail/niche models over time.
- Do NOT scrape manufacturer websites without checking their terms of service —
  prefer manual entry from publicly published spec sheets, or reach out to
  smaller manufacturers directly (a solo founder cold-emailing 20 EV companies
  for spec confirmation is very doable and also good early relationship-building
  for Phase 2 charger-data partnerships).

## 2. Route/Map Data

Use an existing routing provider rather than building road network data
yourself:

| Option              | Pros                                        | Cons                                  |
|----------------------|----------------------------------------------|------------------------------------------|
| Google Maps Directions API | Best India road data & traffic accuracy | Costs scale with usage; needs billing setup |
| Mapbox Directions API | Good coverage, more generous free tier      | Slightly less accurate in India vs Google |
| OSRM (self-hosted, OpenStreetMap data) | Free, full control, no per-request cost | You manage the server; OSM road data quality varies in India, especially rural areas |

**Recommendation:** Start with Google Maps Directions API for the MVP — India
road coverage is the best available, and cost is manageable at low request
volume for a solo/pre-revenue build. Cache route responses aggressively since
common routes (Bangalore–Goa, Bangalore–Chennai, etc.) will repeat often.

## 3. Charger Location Data

This is the hardest data source and where you should NOT try to be
comprehensive on day one.

**Options, roughly in order of speed-to-build:**

1. **PlugShare's public map data** — has broad India coverage including
   multiple networks. Check their API/data licensing terms before building on
   it; many aggregators use it as a bootstrap layer with attribution.
2. **OCPI (Open Charge Point Interface)** — the open protocol several Indian
   players (e.g. One Bharat Charge) are already building on. If you can consume
   an existing OCPI feed rather than negotiating with each network individually,
   this saves enormous BD effort. Worth investigating whether One Bharat Charge
   or similar offers API access to third-party developers.
2. **Individual network APIs** — Tata Power, Statiq, ChargeZone sometimes expose
   developer/partner APIs. Reach out directly; even without live status, static
   location listings are often shareable.
3. **Manual seeding** — for Phase 1, even a manually compiled CSV of major
   highway charging stops (NH48 Bangalore–Goa corridor, NH44, NH8 etc.) gets you
   a usable MVP for the most common intercity routes, without needing to solve
   full India coverage immediately.

**Recommendation for Phase 1:** manually seed charger data for 3–5 popular
intercity corridors relevant to your own use case (e.g. Bangalore–Goa,
Bangalore–Chennai, Bangalore–Hyderabad) to get a working, demoable product
fast. Expand geographic coverage after validating the core planning experience
works and is useful.

## 4. Legal/ToS note

Before scraping any charging network's app or website for location data, check
their terms of service. Where scraping is disallowed, prefer manual entry from
publicly listed information (their own website's "find a station" page,
government EV portals, etc.) or direct outreach for a data-sharing
conversation — which also builds the relationships you'll need for Phase 2 live
status integration anyway.