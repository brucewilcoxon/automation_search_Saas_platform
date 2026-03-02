"""
Report metadata model.
"""
from sqlalchemy import Column, String, ForeignKey, DateTime, Text, Integer
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from backend.app.core.database import Base


class Report(Base):
    """Report metadata entity."""
    __tablename__ = "reports"
    
    id = Column(String, primary_key=True, index=True)
    report_type = Column(String, nullable=False)  # e.g., "auction_pdf"
    parcel_id = Column(String, ForeignKey("parcels.id"), nullable=True)
    event_id = Column(String, ForeignKey("auction_events.id"), nullable=True)
    file_path = Column(String, nullable=True)  # Path to stored PDF file
    file_size = Column(Integer, nullable=True)  # File size in bytes
    status = Column(String, nullable=False, default="pending")  # pending, completed, failed
    error_message = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    parcel = relationship("Parcel", foreign_keys=[parcel_id])
    event = relationship("AuctionEvent", foreign_keys=[event_id])
