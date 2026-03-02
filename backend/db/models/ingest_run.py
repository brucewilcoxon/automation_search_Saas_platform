"""
Ingest run model.
"""
from sqlalchemy import Column, String, Integer, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from backend.app.core.database import Base


class IngestRun(Base):
    """Ingestion run entity for tracking scraper runs."""
    __tablename__ = "ingest_runs"
    
    id = Column(String, primary_key=True, index=True)
    source = Column(String, nullable=False, index=True)
    source_id = Column(String, ForeignKey("auction_sources.id"), nullable=True)
    status = Column(String, nullable=False, default="running", index=True)  # running, completed, failed
    started_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    completed_at = Column(DateTime(timezone=True), nullable=True)
    parcels_processed = Column(Integer, nullable=False, default=0)
    parcels_total = Column(Integer, nullable=True)
    errors = Column(Integer, nullable=False, default=0)
    
    # Relationships
    auction_source = relationship("AuctionSource", foreign_keys=[source_id])
