# Route & Range Planning Engine — Design

## 1. Inputs

- `vehicle_id` (from vehicle DB)
- `origin` (lat/lng or place search)
- `destination` (lat/lng or place search)
- `assumed_avg_speed_kmph` (user-adjustable, default e.g. 60 km/h)
- `starting_battery_pct` (default 100%, user-adjustable)
- `safety_buffer_pct` (default 15–20% — never plan to arrive at a charger below this)

## 2. Pipeline

### Step 1 — Get the route
Call the routing provider (Google Directions API in MVP) with origin +
destination. Returns:
- Polyline of the route
- Total distance (km)
- Base duration estimate (provider's own traffic-based estimate)

### Step 2 — Compute vehicle consumption
Look up the vehicle's `efficiency_wh_per_km` at the closest `speed_band_kmph` to
`assumed_avg_speed_kmph` from the `efficiency_curve` table (interpolate if
needed). Compute:

```
usable_battery_wh = battery_capacity_kwh * 1000 * (starting_battery_pct / 100)
max_range_km = usable_battery_wh / efficiency_wh_per_km
```

### Step 3 — Find candidate chargers along the route
Query the charger DB for stations within a buffer distance (e.g. 3–5 km) of the
route polyline. For each, compute:
- Distance along the route from origin (km marker)
- Connector compatibility with the vehicle (match `dc_charge_port_type` /
  `ac_charge_port_type`)
- Power rating (kW) — filter out chargers too slow to be useful for a road trip
  stop unless no better option exists

### Step 4 — Greedy stop selection
Simple greedy algorithm (good enough for MVP, can be replaced with a proper
shortest-path/optimization later):

```
current_km = 0
current_battery_pct = starting_battery_pct
stops = []

while current_km + range_remaining_km(current_battery_pct) < total_distance:
    # Find the furthest reachable compatible charger before battery
    # drops below safety_buffer_pct
    next_stop = furthest_compatible_charger_within_safe_range(
        current_km, current_battery_pct, safety_buffer_pct
    )
    if next_stop is None:
        flag_route_as_unreachable_with_current_chargers()
        break
    charge_needed_pct = target_pct_for_next_leg(next_stop, ...)
    stops.append({
        "charger": next_stop,
        "km_marker": next_stop.km_from_origin,
        "arrival_battery_pct": ...,
        "charge_to_pct": charge_needed_pct,
        "estimated_charge_time_min": estimate_charge_time(
            vehicle, next_stop.power_kw, arrival_pct, charge_needed_pct
        ),
    })
    current_km = next_stop.km_from_origin
    current_battery_pct = charge_needed_pct
```

### Step 5 — Estimate charge time per stop
Charging isn't linear (fast 10–80%, slow above 80% on DC fast charging).
Simplify for MVP:

```
if using_dc_fast_charger and target_pct <= 80:
    # near-linear approximation is acceptable for 10-80% range
    charge_time_min = (target_pct - arrival_pct) / 100 * battery_capacity_kwh
                       / min(vehicle.max_dc_charge_kw, charger.power_kw) * 60
else:
    # apply a slowdown multiplier above 80% (charging curve tapers)
    ...
```
Refine this with real charge-curve data per vehicle chemistry later (LFP vs
NMC taper differently) — flag as a known simplification in MVP.

### Step 6 — Assemble the itinerary
Output a structured itinerary:

```json
{
  "total_distance_km": 560,
  "assumed_avg_speed_kmph": 60,
  "total_estimated_duration_min": 660,
  "legs": [
    {
      "from_km": 0,
      "to_km": 210,
      "duration_min": 210,
      "battery_start_pct": 100,
      "battery_end_pct": 22,
      "stop": {
        "charger_name": "Statiq - NH48 Hassan",
        "km_marker": 210,
        "charge_from_pct": 22,
        "charge_to_pct": 80,
        "estimated_charge_time_min": 35
      }
    },
    ...
  ]
}
```

This maps directly to the "at this point, at this kilometer, this much charge
will be used" UI requirement.

## 3. Handling "no viable route" gracefully

If no compatible charger exists within safe range at some point, the UI should
say so clearly (e.g. "No compatible fast charger found between km 340–410 for
this vehicle — consider a vehicle with longer range or check for AC charging
options nearby") rather than silently failing or showing a broken plan. This
is a common real failure mode on rural highway stretches in India today, and
handling it gracefully is a trust-building feature, not an edge case to ignore.

## 4. Future refinement (Phase 2+)

- Replace greedy algorithm with a proper optimization (minimize total trip
  time factoring in charge speed vs. distance to next options, not just
  "furthest reachable").
- Factor in elevation/terrain (a big deal on ghat sections, e.g. routes through
  the Western Ghats toward Goa).
- Factor in AC use, cargo load, and passenger count as consumption modifiers.
- Live charger status feeding into stop selection (skip occupied/broken
  chargers dynamically).