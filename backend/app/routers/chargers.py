from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func, select
from sqlalchemy.orm import Session, joinedload

from app.core.database import get_db
from app.models import Charger, ChargerNetwork, ConnectorType, ChargerStatus
from app.schemas import (
    ChargerNetworkCreate,
    ChargerNetworkResponse,
    ChargerCreate,
    ChargerUpdate,
    ChargerResponse,
    ChargerListResponse,
)

router = APIRouter(prefix="/chargers", tags=["chargers"])


@router.get("/networks", response_model=List[ChargerNetworkResponse])
def list_networks(db: Session = Depends(get_db)):
    networks = db.execute(select(ChargerNetwork).order_by(ChargerNetwork.name)).scalars().all()
    return [ChargerNetworkResponse.model_validate(n) for n in networks]


@router.post("/networks", response_model=ChargerNetworkResponse, status_code=status.HTTP_201_CREATED)
def create_network(network: ChargerNetworkCreate, db: Session = Depends(get_db)):
    db_network = ChargerNetwork(**network.model_dump())
    db.add(db_network)
    db.commit()
    db.refresh(db_network)
    return ChargerNetworkResponse.model_validate(db_network)


@router.get("", response_model=ChargerListResponse)
def list_chargers(
    db: Session = Depends(get_db),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    network_id: Optional[UUID] = None,
    connector_type: Optional[ConnectorType] = None,
    min_power_kw: Optional[float] = None,
    status: Optional[ChargerStatus] = None,
    lat: Optional[float] = None,
    lng: Optional[float] = None,
    radius_km: Optional[float] = None,
):
    query = select(Charger).options(joinedload(Charger.network))

    if network_id:
        query = query.where(Charger.network_id == network_id)
    if connector_type:
        query = query.where(Charger.connector_types.ilike(f"%{connector_type.value}%"))
    if min_power_kw:
        query = query.where(Charger.power_kw >= min_power_kw)
    if status:
        query = query.where(Charger.status == status)

    # Simple bounding box filter for nearby chargers (PostGIS would be better for production)
    if lat is not None and lng is not None and radius_km is not None:
        # Rough approximation: 1 degree ~ 111 km
        lat_delta = radius_km / 111.0
        lng_delta = radius_km / (111.0 * max(0.01, abs(lat)))
        query = query.where(
            Charger.latitude.between(lat - lat_delta, lat + lat_delta),
            Charger.longitude.between(lng - lng_delta, lng + lng_delta)
        )

    total = db.execute(select(func.count()).select_from(query.subquery())).scalar()

    chargers = db.execute(
        query.order_by(Charger.name)
        .offset((page - 1) * page_size)
        .limit(page_size)
    ).unique().scalars().all()

    return ChargerListResponse(
        chargers=[ChargerResponse.model_validate(c) for c in chargers],
        total=total,
        page=page,
        page_size=page_size,
    )


@router.get("/{charger_id}", response_model=ChargerResponse)
def get_charger(charger_id: UUID, db: Session = Depends(get_db)):
    charger = db.execute(
        select(Charger).options(joinedload(Charger.network)).where(Charger.id == charger_id)
    ).unique().scalar_one_or_none()
    if not charger:
        raise HTTPException(status_code=404, detail="Charger not found")
    return ChargerResponse.model_validate(charger)


@router.post("", response_model=ChargerResponse, status_code=status.HTTP_201_CREATED)
def create_charger(charger: ChargerCreate, db: Session = Depends(get_db)):
    data = charger.model_dump()
    data["connector_types"] = ",".join([c.value for c in charger.connector_types])
    db_charger = Charger(**data)
    db.add(db_charger)
    db.commit()
    db.refresh(db_charger)
    return ChargerResponse.model_validate(db_charger)


@router.patch("/{charger_id}", response_model=ChargerResponse)
def update_charger(charger_id: UUID, charger: ChargerUpdate, db: Session = Depends(get_db)):
    db_charger = db.get(Charger, charger_id)
    if not db_charger:
        raise HTTPException(status_code=404, detail="Charger not found")

    update_data = charger.model_dump(exclude_unset=True)
    if "connector_types" in update_data:
        update_data["connector_types"] = ",".join([c.value for c in update_data["connector_types"]])

    for field, value in update_data.items():
        setattr(db_charger, field, value)

    db.commit()
    db.refresh(db_charger)
    return ChargerResponse.model_validate(db_charger)


@router.delete("/{charger_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_charger(charger_id: UUID, db: Session = Depends(get_db)):
    db_charger = db.get(Charger, charger_id)
    if not db_charger:
        raise HTTPException(status_code=404, detail="Charger not found")
    db.delete(db_charger)
    db.commit()