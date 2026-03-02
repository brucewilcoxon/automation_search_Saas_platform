"""
Pydantic schemas for cash buyer endpoints.
"""
from pydantic import BaseModel


class CashBuyerResponse(BaseModel):
    """Response schema matching frontend CashBuyer interface."""
    id: str
    name: str
    company: str
    phone: str
    email: str
    county: str
    state: str
    totalPurchases: int
    lastActive: str
    
    class Config:
        from_attributes = True
