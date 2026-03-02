"""
Auction events endpoints.
"""
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import Optional, List
from backend.app.core.database import get_db
from backend.db.models import AuctionEvent, AuctionSource, County
from backend.db.models.auction_item import AuctionItem
from backend.app.schemas.auctions import AuctionEventResponse

router = APIRouter()


@router.get("/auctions", response_model=List[AuctionEventResponse])
async def get_auctions(
    state: Optional[str] = Query(None, description="Filter by state code (e.g., 'FL', 'TX')"),
    county: Optional[str] = Query(None, description="Filter by county name"),
    db: Session = Depends(get_db)
):
    """
    Get auction events with optional filtering by state and county.
    Returns data matching the frontend Auction interface shape.
    """
    query = db.query(AuctionEvent)
    
    if state:
        query = query.filter(AuctionEvent.state == state.upper())
    
    if county:
        query = query.filter(AuctionEvent.county.ilike(f"%{county}%"))
    
    events = query.all()
    
    # Transform to match frontend Auction shape
    results = []
    for event in events:
        # Count items for this event
        item_count = db.query(func.count(AuctionItem.id)).filter(
            AuctionItem.event_id == event.id
        ).scalar() or 0
        
        results.append(AuctionEventResponse(
            id=event.id,
            county=event.county,
            state=event.state,
            date=event.event_date.isoformat() if event.event_date else "",
            totalParcels=item_count,
            status=event.status,
            source=event.source.name if event.source else "Unknown"
        ))
    
    return results
