from typing import Optional, List, Union
from uuid import UUID
from pydantic import BaseModel, Field
from enum import Enum


class ConnectorType(str, Enum):
    TYPE2 = "Type 2"
    BHARAT_AC_001 = "Bharat AC-001"
    CCS2 = "CCS2"
    GB_T = "GB/T"
    BHARAT_DC_001 = "Bharat DC-001"
    CHADEMO = "CHAdeMO"
    TESLA_NACS = "Tesla NACS"


class ChargerStatus(str, Enum):
    UNKNOWN = "unknown"
    OPERATIONAL = "operational"
    OUT_OF_ORDER = "out_of_order"
    MAINTENANCE = "maintenance"


class ChargerNetworkBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    slug: str = Field(..., min_length=1, max_length=100)
    website: Optional[str] = Field(None, max_length=255)
    api_endpoint: Optional[str] = Field(None, max_length=255)
    ocpi_endpoint: Optional[str] = Field(None, max_length=255)
    is_active: int = 1


class ChargerNetworkCreate(ChargerNetworkBase):
    pass


class ChargerNetworkResponse(ChargerNetworkBase):
    id: UUID

    class Config:
        from_attributes = True


class ChargerBase(BaseModel):
    network_id: Optional[UUID] = None
    name: str = Field(..., min_length=1, max_length=200)
    address: Optional[str] = None
    latitude: float = Field(..., ge=-90, le=90)
    longitude: float = Field(..., ge=-180, le=180)
    connector_types: str
    power_kw: float = Field(..., gt=0)
    status: ChargerStatus = ChargerStatus.UNKNOWN
    notes: Optional[str] = None


class ChargerCreate(ChargerBase):
    pass


class ChargerUpdate(BaseModel):
    network_id: Optional[UUID] = None
    name: Optional[str] = Field(None, min_length=1, max_length=200)
    address: Optional[str] = None
    latitude: Optional[float] = Field(None, ge=-90, le=90)
    longitude: Optional[float] = Field(None, ge=-180, le=180)
    connector_types: Optional[str] = None
    power_kw: Optional[float] = Field(None, gt=0)
    status: Optional[ChargerStatus] = None
    notes: Optional[str] = None


class ChargerResponse(ChargerBase):
    id: UUID
    network: Optional[ChargerNetworkResponse] = None

    class Config:
        from_attributes = True


class ChargerListResponse(BaseModel):
    chargers: List[ChargerResponse]
    total: int
    page: int
    page_size: int