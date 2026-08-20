# Vehicle Database — Schema & Structure

## 1. Vehicle Categories

- `two_wheeler` — electric scooters/motorcycles (Ola, Ather, TVS, Bajaj, Hero, etc.)
- `three_wheeler` — electric autos/cargo (Mahindra, Piaggio, Euler, YC Electric, etc.)
- `four_wheeler` — electric cars (Tata, MG, Hyundai, Mahindra, BYD, etc.)

## 2. Core Table: `vehicles`

| Field                     | Type      | Notes                                                     |
|---------------------------|-----------|------------------------------------------------------------|
| id                        | UUID      | Primary key                                                |
| category                  | enum      | two_wheeler / three_wheeler / four_wheeler                 |
| make                      | string    | e.g. "Tata", "Ola Electric", "Mahindra"                     |
| model                     | string    | e.g. "Nexon EV", "S1 Pro"                                   |
| variant                   | string    | e.g. "Long Range", "Prime"                                  |
| model_year                | int       | e.g. 2026                                                   |
| battery_capacity_kwh      | float     | usable capacity                                             |
| battery_chemistry         | string    | LFP / NMC / etc. (affects charge curve, degradation)        |
| arai_range_km             | int       | official certified range                                    |
| real_world_range_km       | int       | curated estimate — see sourcing doc                         |
| top_speed_kmph            | int       |                                                              |
| efficiency_wh_per_km      | float     | at a stated reference speed (store speed_band alongside)    |
| ac_charge_port_type       | string    | e.g. Type 2, Bharat AC-001                                   |
| dc_charge_port_type       | string    | e.g. CCS2, GB/T, Bharat DC-001 (esp. relevant for 2W/3W)     |
| max_ac_charge_kw          | float     |                                                              |
| max_dc_charge_kw          | float     | null if no DC fast charging support (many 2W lack this)     |
| dc_10_80_time_minutes     | int       | nullable                                                    |
| price_ex_showroom_inr     | int       | nullable, for reference/filtering                            |
| status                    | enum      | active / discontinued                                       |
| source_last_verified      | date      | when specs were last checked against manufacturer data       |

## 3. Table: `efficiency_curve` (optional, for accuracy)

Since range varies heavily by speed, terrain, AC use, and load — a single range
number is a simplification. This table lets you store multiple data points per
vehicle.

| Field           | Type  | Notes                                  |
|-----------------|-------|------------------------------------------|
| vehicle_id      | UUID  | FK to vehicles                            |
| speed_band_kmph | int   | e.g. 40, 60, 80, 100                       |
| wh_per_km       | float | consumption at that speed band             |
| source          | enum  | manufacturer / community / estimated       |

This is what powers the "at a speed of 60 km/h, you'll use X% battery over Y km"
calculation the user asked for. Start with manufacturer-published efficiency
figures where available, and a reasonable interpolation/estimation model
elsewhere (see `03-data-sourcing-strategy.md`).

## 4. Table: `range_confidence`

Track how reliable each vehicle's range data is — important for trust, and for
knowing where you need to backfill with community data later.

| Field         | Type  | Notes                                        |
|---------------|-------|-----------------------------------------------|
| vehicle_id    | UUID  |                                                |
| confidence    | enum  | high (ARAI + real-world verified) / medium (ARAI only) / low (manufacturer claim only) |

## 5. Why split ARAI vs real-world range

ARAI test-cycle range is usually 15–25% higher than what drivers actually get in
mixed city/highway conditions with AC on. If the route planner only uses ARAI
numbers, users will run out of charge before your app's predicted stop — this is
the single most trust-destroying bug you could ship. Always default trip
calculations to `real_world_range_km` or the efficiency curve, and clearly
label ARAI figures as "official rated range" in the UI, separate from "expected
range" used for planning.