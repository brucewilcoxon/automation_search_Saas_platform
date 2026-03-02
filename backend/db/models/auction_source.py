"""
Auction source model.
"""
from sqlalchemy import Column, String, Text, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from backend.app.core.database import Base


class AuctionSource(Base):
    """Auction source entity (e.g., County Treasurer, Tax Deed Sale)."""
    __tablename__ = "auction_sources"
    
    id = Column(String, primary_key=True, index=True)
    name = Column(String, nullable=False, unique=True, index=True)
    description = Column(Text, nullable=True)
    source_url_template = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    events = relationship("AuctionEvent", back_populates="source")
