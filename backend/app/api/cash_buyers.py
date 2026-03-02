"""
Cash buyers endpoints.
"""
from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from typing import Optional, List
from datetime import date
from backend.app.core.database import get_db
from backend.db.models.cash_buyer import CashBuyer
from backend.app.schemas.cash_buyers import CashBuyerResponse

router = APIRouter()


@router.get("/cash-buyers", response_model=List[CashBuyerResponse])
async def get_cash_buyers(
    state: Optional[str] = Query(None, description="Filter by state code"),
    county: Optional[str] = Query(None, description="Filter by county name"),
    date_from: Optional[str] = Query(None, description="Filter by last purchase date from (YYYY-MM-DD)"),
    date_to: Optional[str] = Query(None, description="Filter by last purchase date to (YYYY-MM-DD)"),
    min_volume: Optional[float] = Query(None, description="Minimum total volume"),
    q: Optional[str] = Query(None, description="Search query for name, company, or location"),
    db: Session = Depends(get_db)
):
    """
    Get cash buyers with optional filtering.
    
    Supports filtering by:
    - state: State code (e.g., 'FL')
    - county: County name
    - date_from: Last purchase date from
    - date_to: Last purchase date to
    - min_volume: Minimum total volume
    - q: Search query (searches name, company, county, state)
    """
    query = db.query(CashBuyer)
    
    # Apply filters
    if state:
        query = query.filter(CashBuyer.state == state.upper())
    
    if county:
        query = query.filter(CashBuyer.county.ilike(f"%{county}%"))
    
    if date_from:
        try:
            date_from_obj = date.fromisoformat(date_from)
            query = query.filter(CashBuyer.last_purchase_date >= date_from_obj)
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid date_from format. Use YYYY-MM-DD")
    
    if date_to:
        try:
            date_to_obj = date.fromisoformat(date_to)
            query = query.filter(CashBuyer.last_purchase_date <= date_to_obj)
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid date_to format. Use YYYY-MM-DD")
    
    if min_volume:
        query = query.filter(CashBuyer.total_volume >= min_volume)
    
    if q:
        search_term = f"%{q.lower()}%"
        query = query.filter(
            or_(
                CashBuyer.name.ilike(search_term),
                CashBuyer.company.ilike(search_term),
                CashBuyer.county.ilike(search_term),
                CashBuyer.state.ilike(search_term)
            )
        )
    
    # Order by purchase count (most active first)
    buyers = query.order_by(CashBuyer.purchase_count.desc(), CashBuyer.last_purchase_date.desc()).all()
    
    return [
        CashBuyerResponse(
            id=buyer.id,
            name=buyer.name,
            company=buyer.company or "",
            phone=buyer.phone or "",
            email=buyer.email or "",
            county=buyer.county or "",
            state=buyer.state or "",
            totalPurchases=buyer.purchase_count,
            lastActive=buyer.last_purchase_date.isoformat() if buyer.last_purchase_date else ""
        )
        for buyer in buyers
    ]
