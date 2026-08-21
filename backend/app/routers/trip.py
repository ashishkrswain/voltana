from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models import Vehicle
from app.services import TripPlanner, TripInput, TripItinerary

router = APIRouter(prefix="/trip", tags=["trip"])


class TripPlanRequest(BaseModel):
    vehicle_id: UUID
    origin_lat: float = Field(..., ge=-90, le=90)
    origin_lng: float = Field(..., ge=-180, le=180)
    dest_lat: float = Field(..., ge=-90, le=90)
    dest_lng: float = Field(..., ge=-180, le=180)
    assumed_avg_speed_kmph: float = Field(60.0, ge=20, le=120)
    starting_battery_pct: float = Field(100.0, ge=10, le=100)
    safety_buffer_pct: float = Field(20.0, ge=5, le=50)


class TripStopResponse(BaseModel):
    charger_name: str
    km_marker: float
    arrival_battery_pct: float
    charge_to_pct: float
    estimated_charge_time_min: float
    charger_id: str
    charger_address: Optional[str] = None
    network_name: Optional[str] = None
    network_slug: Optional[str] = None
    power_kw: float = 0.0
    latitude: float = 0.0
    longitude: float = 0.0
    connector_types: str = ""


class TripLegResponse(BaseModel):
    from_km: float
    to_km: float
    duration_min: float
    battery_start_pct: float
    battery_end_pct: float
    stop: Optional[TripStopResponse] = None


class TripPlanResponse(BaseModel):
    total_distance_km: float
    assumed_avg_speed_kmph: float
    total_estimated_duration_min: float
    legs: list[TripLegResponse]
    polyline_coords: list[list[float]] = Field(default_factory=list)


@router.post("/plan", response_model=TripPlanResponse)
async def plan_trip(request: TripPlanRequest, db: Session = Depends(get_db)):
    """Plan an EV trip with charging stops."""
    vehicle = db.get(Vehicle, request.vehicle_id)
    if not vehicle:
        raise HTTPException(status_code=404, detail="Vehicle not found")

    planner = TripPlanner(db)

    trip_input = TripInput(
        vehicle=vehicle,
        origin_lat=request.origin_lat,
        origin_lng=request.origin_lng,
        dest_lat=request.dest_lat,
        dest_lng=request.dest_lng,
        assumed_avg_speed_kmph=request.assumed_avg_speed_kmph,
        starting_battery_pct=request.starting_battery_pct,
        safety_buffer_pct=request.safety_buffer_pct,
    )

    try:
        itinerary = await planner.plan_trip(trip_input)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    # Convert to response model
    legs = []
    for leg in itinerary.legs:
        stop_resp = None
        if leg.stop:
            stop_resp = TripStopResponse(
                charger_name=leg.stop.charger_name,
                km_marker=leg.stop.km_marker,
                arrival_battery_pct=leg.stop.arrival_battery_pct,
                charge_to_pct=leg.stop.charge_to_pct,
                estimated_charge_time_min=leg.stop.estimated_charge_time_min,
                charger_id=str(leg.stop.charger_id),
                charger_address=leg.stop.charger_address,
                network_name=leg.stop.network_name,
                network_slug=leg.stop.network_slug,
                power_kw=leg.stop.power_kw,
                latitude=leg.stop.latitude,
                longitude=leg.stop.longitude,
                connector_types=leg.stop.connector_types,
            )
        legs.append(TripLegResponse(
            from_km=leg.from_km,
            to_km=leg.to_km,
            duration_min=leg.duration_min,
            battery_start_pct=leg.battery_start_pct,
            battery_end_pct=leg.battery_end_pct,
            stop=stop_resp,
        ))

    polyline_coords_list = [
        [coord[0], coord[1]] for coord in (itinerary.polyline_coords or [])
    ]

    return TripPlanResponse(
        total_distance_km=itinerary.total_distance_km,
        assumed_avg_speed_kmph=itinerary.assumed_avg_speed_kmph,
        total_estimated_duration_min=itinerary.total_estimated_duration_min,
        legs=legs,
        polyline_coords=polyline_coords_list,
    )