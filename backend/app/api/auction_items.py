"""
Auction items endpoints.
"""
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import List
from backend.app.core.database import get_db
from backend.db.models import AuctionItem
from backend.app.schemas.auctions import AuctionItemResponse

router = APIRouter()


@router.get("/auction-items", response_model=List[AuctionItemResponse])
async def get_auction_items(
    event_id: str = Query(..., description="Auction event ID"),
    db: Session = Depends(get_db)
):
    """
    Get auction items for a specific event.
    """
    items = db.query(AuctionItem).filter(AuctionItem.event_id == event_id).all()
    
    return [
        AuctionItemResponse(
            id=item.id,
            eventId=item.event_id,
            parcelIdRaw=item.parcel_id_raw,
            parcelIdNorm=item.parcel_id_norm,
            openingBid=float(item.opening_bid) if item.opening_bid else 0.0,
            status=item.status,
            itemUrl=item.item_url or ""
        )
        for item in items
    ]
