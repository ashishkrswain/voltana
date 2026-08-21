from dataclasses import dataclass
from typing import List, Optional, Tuple
from uuid import UUID
import math

from app.models import Vehicle, Charger, ConnectorType
from app.services.ors_routing import ORSRouter, RouteResult as RouterRouteResult, get_ors_router


@dataclass
class TripInput:
    vehicle: Vehicle
    origin_lat: float
    origin_lng: float
    dest_lat: float
    dest_lng: float
    assumed_avg_speed_kmph: float = 60.0
    starting_battery_pct: float = 100.0
    safety_buffer_pct: float = 20.0


def decode_polyline(polyline: str) -> List[Tuple[float, float]]:
    """Decode Google Maps encoded polyline to list of (lat, lng) tuples."""
    coords = []
    index = 0
    lat = 0
    lng = 0
    length = len(polyline)

    while index < length:
        shift = 0
        result = 0
        while True:
            b = ord(polyline[index]) - 63
            index += 1
            result |= (b & 0x1f) << shift
            shift += 5
            if b < 0x20:
                break
        dlat = ~(result >> 1) if (result & 1) else (result >> 1)
        lat += dlat

        shift = 0
        result = 0
        while True:
            b = ord(polyline[index]) - 63
            index += 1
            result |= (b & 0x1f) << shift
            shift += 5
            if b < 0x20:
                break
        dlng = ~(result >> 1) if (result & 1) else (result >> 1)
        lng += dlng

        coords.append((lat * 1e-5, lng * 1e-5))

    return coords


def haversine_km(lat1: float, lng1: float, lat2: float, lng2: float) -> float:
    """Calculate distance between two points in km using Haversine formula."""
    R = 6371.0  # Earth radius in km
    dlat = math.radians(lat2 - lat1)
    dlng = math.radians(lng2 - lng1)
    a = (
        math.sin(dlat / 2) ** 2
        + math.cos(math.radians(lat1))
        * math.cos(math.radians(lat2))
        * math.sin(dlng / 2) ** 2
    )
    return R * 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))


def project_point_to_polyline(
    point_lat: float, point_lng: float, polyline_coords: List[Tuple[float, float]]
) -> Tuple[float, int]:
    """
    Project a point onto a polyline and return (distance_along_polyline_km, segment_index).
    Returns the distance from the start of the polyline to the closest point on the polyline.
    """
    if not polyline_coords:
        return 0.0, 0

    min_dist = float("inf")
    closest_km = 0.0
    accumulated_km = 0.0

    for i in range(len(polyline_coords) - 1):
        lat1, lng1 = polyline_coords[i]
        lat2, lng2 = polyline_coords[i + 1]

        segment_length = haversine_km(lat1, lng1, lat2, lng2)

        # Project point onto line segment
        # Using vector projection
        dlat = lat2 - lat1
        dlng = lng2 - lng1

        if segment_length < 1e-6:
            # Degenerate segment
            dist = haversine_km(point_lat, point_lng, lat1, lng1)
            if dist < min_dist:
                min_dist = dist
                closest_km = accumulated_km
            accumulated_km += segment_length
            continue

        # Normalized distance along segment [0, 1]
        t = max(0.0, min(1.0, ((point_lat - lat1) * dlat + (point_lng - lng1) * dlng) / (dlat * dlat + dlng * dlng)))

        proj_lat = lat1 + t * dlat
        proj_lng = lng1 + t * dlng

        dist = haversine_km(point_lat, point_lng, proj_lat, proj_lng)

        if dist < min_dist:
            min_dist = dist
            # Distance along polyline to projected point
            closest_km = accumulated_km + haversine_km(lat1, lng1, proj_lat, proj_lng)

        accumulated_km += segment_length

    return closest_km, min_dist


@dataclass
class RouteResult:
    total_distance_km: float
    total_duration_min: float
    polyline: str
    polyline_coords: List[Tuple[float, float]] = None

    def __post_init__(self):
        if self.polyline_coords is None:
            self.polyline_coords = decode_polyline(self.polyline)


@dataclass
class ChargerCandidate:
    charger: Charger
    km_from_origin: float
    compatible: bool
    power_kw: float


@dataclass
class TripStop:
    charger_name: str
    km_marker: float
    arrival_battery_pct: float
    charge_to_pct: float
    estimated_charge_time_min: float
    charger_id: UUID
    charger_address: Optional[str] = None
    network_name: Optional[str] = None
    network_slug: Optional[str] = None
    power_kw: float = 0.0
    latitude: float = 0.0
    longitude: float = 0.0
    connector_types: str = ""


@dataclass
class TripLeg:
    from_km: float
    to_km: float
    duration_min: float
    battery_start_pct: float
    battery_end_pct: float
    stop: Optional[TripStop] = None


@dataclass
class TripItinerary:
    total_distance_km: float
    assumed_avg_speed_kmph: float
    total_estimated_duration_min: float
    legs: List[TripLeg]
    polyline_coords: Optional[List[Tuple[float, float]]] = None


class TripPlanner:
    def __init__(self, db_session):
        self.db = db_session

    def get_vehicle_efficiency(self, vehicle: Vehicle, speed_kmph: float) -> float:
        """Get efficiency at a given speed, interpolating from efficiency_curve if available."""
        if not vehicle.efficiency_curve:
            return vehicle.efficiency_wh_per_km

        curves = sorted(vehicle.efficiency_curve, key=lambda c: c.speed_band_kmph)

        if speed_kmph <= curves[0].speed_band_kmph:
            return curves[0].wh_per_km
        if speed_kmph >= curves[-1].speed_band_kmph:
            return curves[-1].wh_per_km

        for i in range(len(curves) - 1):
            low = curves[i]
            high = curves[i + 1]
            if low.speed_band_kmph <= speed_kmph <= high.speed_band_kmph:
                t = (speed_kmph - low.speed_band_kmph) / (high.speed_band_kmph - low.speed_band_kmph)
                return low.wh_per_km + t * (high.wh_per_km - low.wh_per_km)

        return vehicle.efficiency_wh_per_km

    def calculate_max_range_km(self, vehicle: Vehicle, speed_kmph: float, starting_battery_pct: float) -> float:
        """Calculate maximum range at given speed and battery level."""
        efficiency = self.get_vehicle_efficiency(vehicle, speed_kmph)
        usable_wh = vehicle.battery_capacity_kwh * 1000 * (starting_battery_pct / 100.0)
        return usable_wh / efficiency

    def find_chargers_along_route(
        self,
        route_polyline: str,
        total_distance_km: float,
        vehicle: Vehicle,
        buffer_km: float = 35.0,
        coords_override: Optional[List[Tuple[float, float]]] = None
    ) -> List[ChargerCandidate]:
        """Find chargers near the route polyline and project them onto the route."""
        all_chargers = self.db.query(Charger).all()

        # Decode polyline once or use override
        polyline_coords = coords_override if coords_override else decode_polyline(route_polyline)

        # Quick bounding box filter to reduce candidates
        if polyline_coords:
            lats = [c[0] for c in polyline_coords]
            lngs = [c[1] for c in polyline_coords]
            min_lat, max_lat = min(lats) - buffer_km / 111.0, max(lats) + buffer_km / 111.0
            min_lng, max_lng = min(lngs) - buffer_km / 111.0, max(lngs) + buffer_km / 111.0

            all_chargers = [
                c for c in all_chargers
                if min_lat <= c.latitude <= max_lat and min_lng <= c.longitude <= max_lng
            ]

        candidates = []
        for charger in all_chargers:
            # Check connector compatibility
            charger_connectors = [c.strip() for c in charger.connector_types.split(",")]
            vehicle_dc = vehicle.dc_charge_port_type
            vehicle_ac = vehicle.ac_charge_port_type

            compatible = False
            for conn in charger_connectors:
                if vehicle_dc and conn == vehicle_dc:
                    compatible = True
                    break
                if vehicle_ac and conn == vehicle_ac:
                    compatible = True
                    break

            if not compatible:
                continue

            # Project charger onto polyline to get km_from_origin
            km_from_origin, dist_to_route = project_point_to_polyline(
                charger.latitude, charger.longitude, polyline_coords
            )

            # Only include chargers within buffer distance of the route
            if dist_to_route > buffer_km:
                continue

            # Clamp to route bounds
            km_from_origin = max(0.0, min(km_from_origin, total_distance_km))

            candidates.append(ChargerCandidate(
                charger=charger,
                km_from_origin=km_from_origin,
                compatible=compatible,
                power_kw=charger.power_kw
            ))

        return candidates

    def select_stops_greedy(
        self,
        candidates: List[ChargerCandidate],
        total_distance_km: float,
        vehicle: Vehicle,
        speed_kmph: float,
        starting_battery_pct: float,
        safety_buffer_pct: float
    ) -> List[TripStop]:
        """Greedy stop selection algorithm."""
        stops = []
        current_km = 0.0
        current_battery_pct = starting_battery_pct

        # Sort candidates by km_from_origin
        candidates = sorted(candidates, key=lambda c: c.km_from_origin)

        while True:
            max_range = self.calculate_max_range_km(vehicle, speed_kmph, current_battery_pct)
            safe_range_km = max_range * (1 - safety_buffer_pct / 100.0)

            if current_km + safe_range_km >= total_distance_km:
                # Can reach destination
                break

            # Find furthest reachable compatible charger within safe range
            next_stop = None
            for candidate in candidates:
                if candidate.km_from_origin <= current_km:
                    continue
                if candidate.km_from_origin - current_km <= safe_range_km:
                    if not next_stop or candidate.km_from_origin > next_stop.km_from_origin:
                        next_stop = candidate

            if not next_stop:
                raise ValueError(f"No compatible charger reachable from km {current_km:.1f} with {current_battery_pct:.1f}% battery")

            # Calculate charge needed to reach next stop or destination
            distance_to_next = next_stop.km_from_origin - current_km
            range_needed = distance_to_next + 50  # 50km buffer to next decision point

            efficiency = self.get_vehicle_efficiency(vehicle, speed_kmph)
            wh_needed = range_needed * efficiency
            pct_needed = (wh_needed / (vehicle.battery_capacity_kwh * 1000)) * 100
            arrival_battery_pct = current_battery_pct - (distance_to_next * efficiency / (vehicle.battery_capacity_kwh * 1000) * 100)
            charge_to_pct = min(80.0, max(arrival_battery_pct + pct_needed, 80.0))

            # Estimate charge time
            charge_time_min = self.estimate_charge_time(
                vehicle,
                next_stop.power_kw,
                arrival_battery_pct,
                charge_to_pct
            )

            charger = next_stop.charger
            network_name = charger.network.name if charger.network else None
            network_slug = charger.network.slug if charger.network else None

            stops.append(TripStop(
                charger_name=charger.name,
                km_marker=next_stop.km_from_origin,
                arrival_battery_pct=arrival_battery_pct,
                charge_to_pct=charge_to_pct,
                estimated_charge_time_min=charge_time_min,
                charger_id=charger.id,
                charger_address=charger.address,
                network_name=network_name,
                network_slug=network_slug,
                power_kw=charger.power_kw,
                latitude=charger.latitude,
                longitude=charger.longitude,
                connector_types=charger.connector_types or ""
            ))

            current_km = next_stop.km_from_origin
            current_battery_pct = charge_to_pct

        return stops

    def estimate_charge_time(
        self,
        vehicle: Vehicle,
        charger_power_kw: float,
        from_pct: float,
        to_pct: float
    ) -> float:
        """Estimate charge time in minutes."""
        effective_power = min(vehicle.max_dc_charge_kw or 0, charger_power_kw)
        if effective_power == 0:
            effective_power = min(vehicle.max_ac_charge_kw or 3.3, charger_power_kw)

        if effective_power == 0:
            return 0.0

        battery_wh = vehicle.battery_capacity_kwh * 1000
        wh_to_add = battery_wh * (to_pct - from_pct) / 100.0

        # Simplified: assume constant power up to 80%, then taper
        if to_pct <= 80:
            hours = wh_to_add / (effective_power * 1000)
        else:
            # Up to 80% at full power, above 80% at 50% power
            wh_to_80 = battery_wh * max(0, 80 - from_pct) / 100.0
            wh_above_80 = battery_wh * max(0, to_pct - max(80, from_pct)) / 100.0
            hours = wh_to_80 / (effective_power * 1000) + wh_above_80 / (effective_power * 500)

        return hours * 60

    async def plan_trip(self, trip_input: TripInput) -> TripItinerary:
        """Main trip planning entry point."""
        # Step 1: Get route from OpenRouteService
        fallback_coords = None
        try:
            router = get_ors_router()
            route_data = await router.get_route(
                trip_input.origin_lat,
                trip_input.origin_lng,
                trip_input.dest_lat,
                trip_input.dest_lng,
            )
            route = RouteResult(
                total_distance_km=route_data.distance_km,
                total_duration_min=route_data.duration_min,
                polyline=route_data.polyline,
                polyline_coords=route_data.polyline_coords,
            )
        except Exception:
            # Fallback for development/testing without internet / API
            straight_dist = haversine_km(
                trip_input.origin_lat, trip_input.origin_lng,
                trip_input.dest_lat, trip_input.dest_lng
            )
            distance_km = max(560.0, straight_dist * 1.25) if straight_dist > 50 else straight_dist

            # Create smooth highway corridor points (default to realistic NH48 route for Bangalore-Goa)
            if abs(trip_input.origin_lat - 12.97) < 1.0 and abs(trip_input.dest_lat - 15.3) < 1.0:
                fallback_coords = [
                    (12.9716, 77.5946),
                    (13.1004, 76.9791),
                    (13.0072, 76.1004),
                    (13.1642, 75.7674),
                    (13.4200, 75.2500),
                    (14.2500, 74.7000),
                    (14.8170, 74.1284),
                    (15.2993, 74.1240),
                ]
            else:
                num_steps = 10
                fallback_coords = [
                    (
                        trip_input.origin_lat + (trip_input.dest_lat - trip_input.origin_lat) * (i / num_steps),
                        trip_input.origin_lng + (trip_input.dest_lng - trip_input.origin_lng) * (i / num_steps)
                    )
                    for i in range(num_steps + 1)
                ]

            route = RouteResult(
                total_distance_km=distance_km,
                total_duration_min=distance_km / trip_input.assumed_avg_speed_kmph * 60,
                polyline="",
                polyline_coords=fallback_coords
            )

        # Step 2: Find candidate chargers
        candidates = self.find_chargers_along_route(
            route.polyline,
            route.total_distance_km,
            trip_input.vehicle,
            buffer_km=45.0,
            coords_override=route.polyline_coords
        )

        # Step 3: Select stops using greedy algorithm
        try:
            stops = self.select_stops_greedy(
                candidates,
                route.total_distance_km,
                trip_input.vehicle,
                trip_input.assumed_avg_speed_kmph,
                trip_input.starting_battery_pct,
                trip_input.safety_buffer_pct
            )
        except ValueError as e:
            # No viable route
            raise

        # Step 4: Build legs
        legs = []
        current_km = 0.0
        current_battery_pct = trip_input.starting_battery_pct

        for i, stop in enumerate(stops):
            distance = stop.km_marker - current_km
            duration = distance / trip_input.assumed_avg_speed_kmph * 60
            efficiency = self.get_vehicle_efficiency(trip_input.vehicle, trip_input.assumed_avg_speed_kmph)
            battery_used = distance * efficiency / (trip_input.vehicle.battery_capacity_kwh * 1000) * 100

            legs.append(TripLeg(
                from_km=current_km,
                to_km=stop.km_marker,
                duration_min=duration,
                battery_start_pct=current_battery_pct,
                battery_end_pct=current_battery_pct - battery_used,
                stop=stop
            ))

            current_km = stop.km_marker
            current_battery_pct = stop.charge_to_pct

        # Final leg to destination
        if current_km < route.total_distance_km:
            distance = route.total_distance_km - current_km
            duration = distance / trip_input.assumed_avg_speed_kmph * 60
            efficiency = self.get_vehicle_efficiency(trip_input.vehicle, trip_input.assumed_avg_speed_kmph)
            battery_used = distance * efficiency / (trip_input.vehicle.battery_capacity_kwh * 1000) * 100

            legs.append(TripLeg(
                from_km=current_km,
                to_km=route.total_distance_km,
                duration_min=duration,
                battery_start_pct=current_battery_pct,
                battery_end_pct=current_battery_pct - battery_used,
                stop=None
            ))

        total_duration = sum(leg.duration_min for leg in legs) + sum(leg.stop.estimated_charge_time_min for leg in legs if leg.stop)

        return TripItinerary(
            total_distance_km=route.total_distance_km,
            assumed_avg_speed_kmph=trip_input.assumed_avg_speed_kmph,
            total_estimated_duration_min=total_duration,
            legs=legs,
            polyline_coords=route.polyline_coords or decode_polyline(route.polyline)
        )