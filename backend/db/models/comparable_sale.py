"""
Comparable sale model.
"""
from sqlalchemy import Column, String, Numeric, Date, JSON, Index
from sqlalchemy.orm import relationship
from backend.app.core.database import Base


class ComparableSale(Base):
    """Comparable sale entity for parcel valuation."""
    __tablename__ = "comparable_sales"
    
    id = Column(String, primary_key=True, index=True)
    parcel_id_norm = Column(String, nullable=False, index=True)  # Normalized parcel ID
    comp_id = Column(String, nullable=False, unique=True, index=True)  # Unique comparable sale ID
    sold_date = Column(Date, nullable=False, index=True)
    sold_price = Column(Numeric(12, 2), nullable=False)
    distance = Column(Numeric(10, 4), nullable=True)  # Distance in miles
    similarity_score = Column(Numeric(5, 2), nullable=False)  # 0-100 similarity score
    raw_json = Column(JSON, nullable=True)  # Raw JSON snapshot
    
    # Additional fields for frontend display
    address = Column(String, nullable=True)
    acreage = Column(Numeric(10, 4), nullable=True)  # Area in acres
    zoning = Column(String, nullable=True)
    
    # Relationships
    # Note: parcel_id_norm is a string, not a foreign key, to allow flexibility
    # We use a manual relationship lookup instead
    
    # Index for efficient queries
    __table_args__ = (
        Index('idx_parcel_sold_date', 'parcel_id_norm', 'sold_date'),
    )
