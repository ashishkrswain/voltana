from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models import Vehicle, VehicleCategory, EfficiencyCurve, RangeConfidence
from app.schemas import (
    VehicleCreate,
    VehicleUpdate,
    VehicleResponse,
    VehicleListResponse,
    EfficiencyCurveCreate,
    EfficiencyCurveResponse,
    RangeConfidenceBase,
    RangeConfidenceResponse,
)

router = APIRouter(prefix="/vehicles", tags=["vehicles"])


@router.get("", response_model=VehicleListResponse)
def list_vehicles(
    db: Session = Depends(get_db),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    category: Optional[VehicleCategory] = None,
    make: Optional[str] = None,
    search: Optional[str] = None,
):
    query = select(Vehicle)

    if category:
        query = query.where(Vehicle.category == category)
    if make:
        query = query.where(Vehicle.make.ilike(f"%{make}%"))
    if search:
        query = query.where(
            (Vehicle.make.ilike(f"%{search}%")) |
            (Vehicle.model.ilike(f"%{search}%")) |
            (Vehicle.variant.ilike(f"%{search}%"))
        )

    total = db.execute(select(func.count()).select_from(query.subquery())).scalar()

    vehicles = db.execute(
        query.order_by(Vehicle.make, Vehicle.model, Vehicle.variant)
        .offset((page - 1) * page_size)
        .limit(page_size)
    ).scalars().all()

    return VehicleListResponse(
        vehicles=[VehicleResponse.model_validate(v) for v in vehicles],
        total=total,
        page=page,
        page_size=page_size,
    )


@router.get("/makes", response_model=List[str])
def list_makes(db: Session = Depends(get_db)):
    makes = db.execute(select(Vehicle.make).distinct().order_by(Vehicle.make)).scalars().all()
    return makes


@router.get("/{vehicle_id}", response_model=VehicleResponse)
def get_vehicle(vehicle_id: UUID, db: Session = Depends(get_db)):
    vehicle = db.get(Vehicle, vehicle_id)
    if not vehicle:
        raise HTTPException(status_code=404, detail="Vehicle not found")
    return VehicleResponse.model_validate(vehicle)


@router.post("", response_model=VehicleResponse, status_code=status.HTTP_201_CREATED)
def create_vehicle(vehicle: VehicleCreate, db: Session = Depends(get_db)):
    db_vehicle = Vehicle(**vehicle.model_dump())
    db.add(db_vehicle)
    db.commit()
    db.refresh(db_vehicle)
    return VehicleResponse.model_validate(db_vehicle)


@router.patch("/{vehicle_id}", response_model=VehicleResponse)
def update_vehicle(vehicle_id: UUID, vehicle: VehicleUpdate, db: Session = Depends(get_db)):
    db_vehicle = db.get(Vehicle, vehicle_id)
    if not db_vehicle:
        raise HTTPException(status_code=404, detail="Vehicle not found")

    update_data = vehicle.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_vehicle, field, value)

    db.commit()
    db.refresh(db_vehicle)
    return VehicleResponse.model_validate(db_vehicle)


@router.delete("/{vehicle_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_vehicle(vehicle_id: UUID, db: Session = Depends(get_db)):
    db_vehicle = db.get(Vehicle, vehicle_id)
    if not db_vehicle:
        raise HTTPException(status_code=404, detail="Vehicle not found")
    db.delete(db_vehicle)
    db.commit()


@router.post("/{vehicle_id}/efficiency-curve", response_model=EfficiencyCurveResponse, status_code=status.HTTP_201_CREATED)
def add_efficiency_curve(vehicle_id: UUID, curve: EfficiencyCurveCreate, db: Session = Depends(get_db)):
    vehicle = db.get(Vehicle, vehicle_id)
    if not vehicle:
        raise HTTPException(status_code=404, detail="Vehicle not found")

    db_curve = EfficiencyCurve(vehicle_id=vehicle_id, **curve.model_dump())
    db.add(db_curve)
    db.commit()
    db.refresh(db_curve)
    return EfficiencyCurveResponse.model_validate(db_curve)


@router.put("/{vehicle_id}/range-confidence", response_model=RangeConfidenceResponse)
def upsert_range_confidence(vehicle_id: UUID, confidence: RangeConfidenceBase, db: Session = Depends(get_db)):
    vehicle = db.get(Vehicle, vehicle_id)
    if not vehicle:
        raise HTTPException(status_code=404, detail="Vehicle not found")

    existing = db.get(RangeConfidence, vehicle_id)
    if existing:
        existing.confidence = confidence.confidence
    else:
        existing = RangeConfidence(vehicle_id=vehicle_id, confidence=confidence.confidence)
        db.add(existing)

    db.commit()
    db.refresh(existing)
    return RangeConfidenceResponse.model_validate(existing)