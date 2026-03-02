"""
Auction item model.
"""
from sqlalchemy import Column, String, Numeric, ForeignKey, JSON
from sqlalchemy.orm import relationship
from backend.app.core.database import Base


class AuctionItem(Base):
    """Auction item entity."""
    __tablename__ = "auction_items"
    
    id = Column(String, primary_key=True, index=True)
    event_id = Column(String, ForeignKey("auction_events.id"), nullable=False, index=True)
    parcel_id_raw = Column(String, nullable=True, index=True)
    parcel_id_norm = Column(String, nullable=True, index=True)
    opening_bid = Column(Numeric(12, 2), nullable=True)
    status = Column(String, nullable=False, default="available", index=True)  # available, sold, cancelled, pending
    item_url = Column(String, nullable=True)
    raw_json = Column(JSON, nullable=True)  # Raw JSON snapshot from scraper
    
    # Relationships
    event = relationship("AuctionEvent", back_populates="items")
