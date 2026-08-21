import enum
import uuid
from datetime import date
from typing import Optional

from sqlalchemy import Column, Enum, Float, ForeignKey, Integer, String, Date, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.core.database import Base


class VehicleCategory(str, enum.Enum):
    TWO_WHEELER = "two_wheeler"
    THREE_WHEELER = "three_wheeler"
    FOUR_WHEELER = "four_wheeler"


class VehicleStatus(str, enum.Enum):
    ACTIVE = "active"
    DISCONTINUED = "discontinued"


class RangeConfidenceLevel(str, enum.Enum):
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class EfficiencySource(str, enum.Enum):
    MANUFACTURER = "manufacturer"
    COMMUNITY = "community"
    ESTIMATED = "estimated"


class Vehicle(Base):
    __tablename__ = "vehicles"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    category = Column(Enum(VehicleCategory, values_callable=lambda x: [e.value for e in x]), nullable=False, index=True)
    make = Column(String(100), nullable=False, index=True)
    model = Column(String(100), nullable=False, index=True)
    variant = Column(String(100), nullable=False)
    model_year = Column(Integer, nullable=False)
    battery_capacity_kwh = Column(Float, nullable=False)
    battery_chemistry = Column(String(50))
    arai_range_km = Column(Integer, nullable=False)
    real_world_range_km = Column(Integer, nullable=False)
    top_speed_kmph = Column(Integer)
    efficiency_wh_per_km = Column(Float, nullable=False)
    ac_charge_port_type = Column(String(50))
    dc_charge_port_type = Column(String(50))
    max_ac_charge_kw = Column(Float)
    max_dc_charge_kw = Column(Float, nullable=True)
    dc_10_80_time_minutes = Column(Integer, nullable=True)
    price_ex_showroom_inr = Column(Integer, nullable=True)
    status = Column(Enum(VehicleStatus, values_callable=lambda x: [e.value for e in x]), default=VehicleStatus.ACTIVE, nullable=False)
    source_last_verified = Column(Date)

    efficiency_curve = relationship("EfficiencyCurve", back_populates="vehicle", cascade="all, delete-orphan")
    range_confidence = relationship("RangeConfidence", back_populates="vehicle", uselist=False, cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Vehicle {self.make} {self.model} {self.variant}>"


class EfficiencyCurve(Base):
    __tablename__ = "efficiency_curve"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    vehicle_id = Column(UUID(as_uuid=True), ForeignKey("vehicles.id", ondelete="CASCADE"), nullable=False, index=True)
    speed_band_kmph = Column(Integer, nullable=False)
    wh_per_km = Column(Float, nullable=False)
    source = Column(Enum(EfficiencySource, values_callable=lambda x: [e.value for e in x]), default=EfficiencySource.ESTIMATED, nullable=False)

    vehicle = relationship("Vehicle", back_populates="efficiency_curve")

    def __repr__(self):
        return f"<EfficiencyCurve vehicle={self.vehicle_id} speed={self.speed_band_kmph} wh_per_km={self.wh_per_km}>"


class RangeConfidence(Base):
    __tablename__ = "range_confidence"

    vehicle_id = Column(UUID(as_uuid=True), ForeignKey("vehicles.id", ondelete="CASCADE"), primary_key=True)
    confidence = Column(Enum(RangeConfidenceLevel, values_callable=lambda x: [e.value for e in x]), nullable=False)

    vehicle = relationship("Vehicle", back_populates="range_confidence")

    def __repr__(self):
        return f"<RangeConfidence vehicle={self.vehicle_id} confidence={self.confidence}>"