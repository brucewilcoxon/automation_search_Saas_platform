"""
Cash buyer model.
"""
from sqlalchemy import Column, String, Integer, Numeric, Date, JSON, Index
from sqlalchemy.orm import relationship
from backend.app.core.database import Base


class CashBuyer(Base):
    """Cash buyer entity."""
    __tablename__ = "cash_buyers"
    
    id = Column(String, primary_key=True, index=True)
    name = Column(String, nullable=False, index=True)
    company = Column(String, nullable=True, index=True)
    address = Column(String, nullable=True)
    phone = Column(String, nullable=True)
    email = Column(String, nullable=True, index=True)
    county = Column(String, nullable=True, index=True)
    state = Column(String(2), nullable=True, index=True)
    purchase_count = Column(Integer, nullable=False, default=0)  # Number of purchases
    last_purchase_date = Column(Date, nullable=True, index=True)
    total_volume = Column(Numeric(12, 2), nullable=True)  # Total purchase volume in dollars
    raw_json = Column(JSON, nullable=True)  # Raw JSON snapshot
    
    # Index for efficient queries
    __table_args__ = (
        Index('idx_buyer_location', 'county', 'state'),
        Index('idx_buyer_activity', 'last_purchase_date', 'purchase_count'),
    )
