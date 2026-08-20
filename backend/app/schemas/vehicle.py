from datetime import date
from typing import Optional, List
from pydantic import BaseModel, Field
from enum import Enum


class VehicleCategory(str, Enum):
    TWO_WHEELER = "two_wheeler"
    THREE_WHEELER = "three_wheeler"
    FOUR_WHEELER = "four_wheeler"


class VehicleStatus(str, Enum):
    ACTIVE = "active"
    DISCONTINUED = "discontinued"


class RangeConfidenceLevel(str, Enum):
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class EfficiencySource(str, Enum):
    MANUFACTURER = "manufacturer"
    COMMUNITY = "community"
    ESTIMATED = "estimated"


class EfficiencyCurveBase(BaseModel):
    speed_band_kmph: int = Field(..., ge=0)
    wh_per_km: float = Field(..., gt=0)
    source: EfficiencySource = EfficiencySource.ESTIMATED


class EfficiencyCurveCreate(EfficiencyCurveBase):
    pass


class EfficiencyCurveResponse(EfficiencyCurveBase):
    id: str
    vehicle_id: str

    class Config:
        from_attributes = True


class RangeConfidenceBase(BaseModel):
    confidence: RangeConfidenceLevel


class RangeConfidenceResponse(RangeConfidenceBase):
    vehicle_id: str

    class Config:
        from_attributes = True


class VehicleBase(BaseModel):
    category: VehicleCategory
    make: str = Field(..., min_length=1, max_length=100)
    model: str = Field(..., min_length=1, max_length=100)
    variant: str = Field(..., min_length=1, max_length=100)
    model_year: int = Field(..., ge=2010, le=2030)
    battery_capacity_kwh: float = Field(..., gt=0)
    battery_chemistry: Optional[str] = Field(None, max_length=50)
    arai_range_km: int = Field(..., gt=0)
    real_world_range_km: int = Field(..., gt=0)
    top_speed_kmph: Optional[int] = Field(None, ge=0)
    efficiency_wh_per_km: float = Field(..., gt=0)
    ac_charge_port_type: Optional[str] = Field(None, max_length=50)
    dc_charge_port_type: Optional[str] = Field(None, max_length=50)
    max_ac_charge_kw: Optional[float] = Field(None, ge=0)
    max_dc_charge_kw: Optional[float] = Field(None, ge=0)
    dc_10_80_time_minutes: Optional[int] = Field(None, ge=0)
    price_ex_showroom_inr: Optional[int] = Field(None, ge=0)
    status: VehicleStatus = VehicleStatus.ACTIVE
    source_last_verified: Optional[date] = None


class VehicleCreate(VehicleBase):
    pass


class VehicleUpdate(BaseModel):
    category: Optional[VehicleCategory] = None
    make: Optional[str] = Field(None, min_length=1, max_length=100)
    model: Optional[str] = Field(None, min_length=1, max_length=100)
    variant: Optional[str] = Field(None, min_length=1, max_length=100)
    model_year: Optional[int] = Field(None, ge=2010, le=2030)
    battery_capacity_kwh: Optional[float] = Field(None, gt=0)
    battery_chemistry: Optional[str] = Field(None, max_length=50)
    arai_range_km: Optional[int] = Field(None, gt=0)
    real_world_range_km: Optional[int] = Field(None, gt=0)
    top_speed_kmph: Optional[int] = Field(None, ge=0)
    efficiency_wh_per_km: Optional[float] = Field(None, gt=0)
    ac_charge_port_type: Optional[str] = Field(None, max_length=50)
    dc_charge_port_type: Optional[str] = Field(None, max_length=50)
    max_ac_charge_kw: Optional[float] = Field(None, ge=0)
    max_dc_charge_kw: Optional[float] = Field(None, ge=0)
    dc_10_80_time_minutes: Optional[int] = Field(None, ge=0)
    price_ex_showroom_inr: Optional[int] = Field(None, ge=0)
    status: Optional[VehicleStatus] = None
    source_last_verified: Optional[date] = None


class VehicleResponse(VehicleBase):
    id: str
    efficiency_curve: List[EfficiencyCurveResponse] = []
    range_confidence: Optional[RangeConfidenceResponse] = None

    class Config:
        from_attributes = True


class VehicleListResponse(BaseModel):
    vehicles: List[VehicleResponse]
    total: int
    page: int
    page_size: int