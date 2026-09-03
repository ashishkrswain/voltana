from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field


class TripCreate(BaseModel):
    vehicle_id: UUID
    origin_name: str = Field(..., min_length=1, max_length=200)
    origin_lat: float = Field(..., ge=-90, le=90)
    origin_lng: float = Field(..., ge=-180, le=180)
    dest_name: str = Field(..., min_length=1, max_length=200)
    dest_lat: float = Field(..., ge=-90, le=90)
    dest_lng: float = Field(..., ge=-180, le=180)
    assumed_avg_speed_kmph: float = Field(60.0, ge=20, le=120)
    starting_battery_pct: float = Field(100.0, ge=10, le=100)
    safety_buffer_pct: float = Field(20.0, ge=5, le=50)
    total_distance_km: float = Field(..., ge=0)
    total_estimated_duration_min: float = Field(..., ge=0)


class TripResponse(TripCreate):
    id: UUID
    created_at: datetime
    vehicle_make: Optional[str] = None
    vehicle_model: Optional[str] = None
    vehicle_variant: Optional[str] = None

    class Config:
        from_attributes = True


class TripListResponse(BaseModel):
    trips: list[TripResponse]
    total: int
