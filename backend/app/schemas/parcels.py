"""
Pydantic schemas for parcel-related endpoints.
"""
from pydantic import BaseModel
from typing import Optional


class ParcelResponse(BaseModel):
    """Response schema matching frontend Parcel interface."""
    id: str
    auctionId: str
    apn: str
    address: str
    county: str
    state: str
    acreage: float
    marketValue: float
    minBid: float
    zoning: str
    status: str  # "available" | "sold" | "withdrawn"
    latitude: float
    longitude: float
    # Milestone 3 fields
    taxes: Optional[float] = None
    assessedValue: Optional[float] = None
    floodFlag: Optional[bool] = None
    lastUpdatedAt: Optional[str] = None
    
    class Config:
        from_attributes = True


class ComparableSaleResponse(BaseModel):
    """Response schema matching frontend CompSale interface."""
    address: str
    area: str  # e.g., "2.1 ac"
    price: float
    date: str  # ISO date string
    distance: str  # e.g., "0.9 mi"
    similarity: int  # 0-100 similarity score
    
    class Config:
        from_attributes = True
