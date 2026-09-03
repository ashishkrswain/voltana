import uuid
from datetime import datetime
from typing import Optional

from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, String, Text, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.core.database import Base


class SavedTrip(Base):
    """A past route-plan result, saved so the user can re-plan it later."""

    __tablename__ = "saved_trips"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    vehicle_id = Column(UUID(as_uuid=True), ForeignKey("vehicles.id", ondelete="CASCADE"), nullable=False, index=True)
    origin_name = Column(String(200), nullable=False)
    origin_lat = Column(Float, nullable=False)
    origin_lng = Column(Float, nullable=False)
    dest_name = Column(String(200), nullable=False)
    dest_lat = Column(Float, nullable=False)
    dest_lng = Column(Float, nullable=False)
    assumed_avg_speed_kmph = Column(Float, nullable=False, default=60.0)
    starting_battery_pct = Column(Float, nullable=False, default=100.0)
    safety_buffer_pct = Column(Float, nullable=False, default=20.0)
    total_distance_km = Column(Float, nullable=False)
    total_estimated_duration_min = Column(Float, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    vehicle = relationship("Vehicle")

    def __repr__(self):
        return f"<SavedTrip {self.origin_name} → {self.dest_name}>"
