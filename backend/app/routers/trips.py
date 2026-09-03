from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func, select
from sqlalchemy.orm import Session, joinedload

from app.core.database import get_db
from app.models import SavedTrip, Vehicle
from app.schemas.trip import TripCreate, TripListResponse, TripResponse

router = APIRouter(prefix="/trips", tags=["trips"])


def _to_response(trip: SavedTrip) -> TripResponse:
    resp = TripResponse.model_validate(trip)
    if trip.vehicle:
        resp.vehicle_make = trip.vehicle.make
        resp.vehicle_model = trip.vehicle.model
        resp.vehicle_variant = trip.vehicle.variant
    return resp


@router.get("", response_model=TripListResponse)
def list_trips(
    db: Session = Depends(get_db),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
):
    query = select(SavedTrip).options(joinedload(SavedTrip.vehicle))
    total = db.execute(select(func.count()).select_from(SavedTrip)).scalar()
    trips = db.execute(
        query.order_by(SavedTrip.created_at.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
    ).unique().scalars().all()

    return TripListResponse(
        trips=[_to_response(t) for t in trips],
        total=total or 0,
    )


@router.post("", response_model=TripResponse, status_code=status.HTTP_201_CREATED)
def create_trip(trip: TripCreate, db: Session = Depends(get_db)):
    vehicle = db.get(Vehicle, trip.vehicle_id)
    if not vehicle:
        raise HTTPException(status_code=404, detail="Vehicle not found")

    db_trip = SavedTrip(**trip.model_dump())
    db.add(db_trip)
    db.commit()
    db.refresh(db_trip)
    db_trip.vehicle = vehicle
    return _to_response(db_trip)


@router.delete("/{trip_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_trip(trip_id: UUID, db: Session = Depends(get_db)):
    trip = db.get(SavedTrip, trip_id)
    if not trip:
        raise HTTPException(status_code=404, detail="Trip not found")
    db.delete(trip)
    db.commit()
