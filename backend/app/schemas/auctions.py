"""
Pydantic schemas for auction-related endpoints.
"""
from pydantic import BaseModel
from typing import Optional


class AuctionEventResponse(BaseModel):
    """Response schema matching frontend Auction interface."""
    id: str
    county: str
    state: str
    date: str
    totalParcels: int
    status: str  # "upcoming" | "live" | "completed"
    source: str
    
    class Config:
        from_attributes = True


class AuctionItemResponse(BaseModel):
    """Response schema matching frontend AuctionItem interface."""
    id: str
    eventId: str
    parcelIdRaw: str
    parcelIdNorm: str
    openingBid: float
    status: str  # "available" | "sold" | "cancelled" | "pending"
    itemUrl: str
    
    class Config:
        from_attributes = True
