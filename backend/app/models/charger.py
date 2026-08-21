import enum
import uuid
from typing import Optional

from sqlalchemy import Column, Enum, Float, ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.core.database import Base


class ConnectorType(str, enum.Enum):
    TYPE2 = "Type 2"
    BHARAT_AC_001 = "Bharat AC-001"
    CCS2 = "CCS2"
    GB_T = "GB/T"
    BHARAT_DC_001 = "Bharat DC-001"
    CHADEMO = "CHAdeMO"
    TESLA_NACS = "Tesla NACS"


class ChargerStatus(str, enum.Enum):
    UNKNOWN = "unknown"
    OPERATIONAL = "operational"
    OUT_OF_ORDER = "out_of_order"
    MAINTENANCE = "maintenance"


class ChargerNetwork(Base):
    __tablename__ = "charger_networks"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(100), unique=True, nullable=False, index=True)
    slug = Column(String(100), unique=True, nullable=False, index=True)
    website = Column(String(255))
    api_endpoint = Column(String(255), nullable=True)
    ocpi_endpoint = Column(String(255), nullable=True)
    is_active = Column(Integer, default=1)

    chargers = relationship("Charger", back_populates="network")

    def __repr__(self):
        return f"<ChargerNetwork {self.name}>"


class Charger(Base):
    __tablename__ = "chargers"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    network_id = Column(UUID(as_uuid=True), ForeignKey("charger_networks.id", ondelete="SET NULL"), nullable=True, index=True)
    name = Column(String(200), nullable=False)
    address = Column(Text)
    latitude = Column(Float, nullable=False, index=True)
    longitude = Column(Float, nullable=False, index=True)
    connector_types = Column(Text, nullable=False)  # JSON array of ConnectorType values
    power_kw = Column(Float, nullable=False)  # max power for this station
    status = Column(Enum(ChargerStatus, values_callable=lambda x: [e.value for e in x]), default=ChargerStatus.UNKNOWN, nullable=False)
    notes = Column(Text, nullable=True)

    network = relationship("ChargerNetwork", back_populates="chargers")

    def __repr__(self):
        return f"<Charger {self.name} ({self.network_id})>"