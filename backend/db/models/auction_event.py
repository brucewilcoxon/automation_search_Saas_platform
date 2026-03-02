"""
Auction event model.
"""
from sqlalchemy import Column, String, Date, ForeignKey, Integer, JSON
from sqlalchemy.orm import relationship
from backend.app.core.database import Base


class AuctionEvent(Base):
    """Auction event entity."""
    __tablename__ = "auction_events"
    
    id = Column(String, primary_key=True, index=True)
    state = Column(String(2), nullable=False, index=True)
    county = Column(String, nullable=False, index=True)
    county_id = Column(String, ForeignKey("counties.id"), nullable=True)
    event_date = Column(Date, nullable=False, index=True)
    status = Column(String, nullable=False, default="upcoming", index=True)  # upcoming, live, ended
    source_id = Column(String, ForeignKey("auction_sources.id"), nullable=True)
    source_url = Column(String, nullable=True)
    item_count = Column(Integer, nullable=True, default=0)
    raw_json = Column(JSON, nullable=True)  # Raw JSON snapshot from scraper
    
    # Relationships
    source = relationship("AuctionSource", back_populates="events")
    county_rel = relationship("County", back_populates="events")
    items = relationship("AuctionItem", back_populates="event", cascade="all, delete-orphan")
