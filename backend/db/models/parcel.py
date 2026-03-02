"""
Parcel model.
"""
from sqlalchemy import Column, String, Numeric, ForeignKey, Boolean, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from backend.app.core.database import Base


class Parcel(Base):
    """Parcel entity."""
    __tablename__ = "parcels"
    
    id = Column(String, primary_key=True, index=True)
    auction_id = Column(String, nullable=True, index=True)
    auction_item_id = Column(String, ForeignKey("auction_items.id"), nullable=True)
    apn = Column(String, nullable=True, index=True)  # Assessor's Parcel Number
    address = Column(String, nullable=True)
    county = Column(String, nullable=True, index=True)
    county_id = Column(String, ForeignKey("counties.id"), nullable=True)
    state = Column(String(2), nullable=True, index=True)
    acreage = Column(Numeric(10, 4), nullable=True)
    market_value = Column(Numeric(12, 2), nullable=True)  # Also used as assessed_value
    min_bid = Column(Numeric(12, 2), nullable=True)
    zoning = Column(String, nullable=True)
    status = Column(String, nullable=False, default="available", index=True)  # available, sold, withdrawn
    latitude = Column(Numeric(10, 7), nullable=True)
    longitude = Column(Numeric(10, 7), nullable=True)
    
    # Milestone 3 fields
    taxes = Column(Numeric(12, 2), nullable=True)  # Annual taxes
    assessed_value = Column(Numeric(12, 2), nullable=True)  # Explicit assessed value (may differ from market_value)
    flood_flag = Column(Boolean, nullable=True, default=False)  # FEMA flood zone flag
    last_updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    county_rel = relationship("County", back_populates="parcels")
    # Comparable sales are linked by parcel_id_norm (APN), not a direct FK
