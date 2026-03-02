"""
County model.
"""
from sqlalchemy import Column, String, Integer
from sqlalchemy.orm import relationship
from backend.app.core.database import Base


class County(Base):
    """County entity."""
    __tablename__ = "counties"
    
    id = Column(String, primary_key=True, index=True)
    name = Column(String, nullable=False, index=True)
    state = Column(String(2), nullable=False, index=True)
    state_full = Column(String, nullable=True)
    fips_code = Column(String, nullable=True)
    
    # Relationships
    events = relationship("AuctionEvent", back_populates="county_rel")
    parcels = relationship("Parcel", back_populates="county_rel")
