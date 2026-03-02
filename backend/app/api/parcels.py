"""
Parcels endpoints.
"""
from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session
from typing import Optional, List
from datetime import date, timedelta
from backend.app.core.database import get_db
from backend.db.models.parcel import Parcel
from backend.db.models.comparable_sale import ComparableSale
from backend.app.schemas.parcels import ParcelResponse, ComparableSaleResponse

router = APIRouter()


@router.get("/parcels", response_model=List[ParcelResponse])
async def get_parcels(
    parcel_id: Optional[str] = Query(None, description="Filter by parcel ID"),
    db: Session = Depends(get_db)
):
    """
    Get parcels with optional filtering by parcel_id.
    """
    query = db.query(Parcel)
    
    if parcel_id:
        query = query.filter(Parcel.id == parcel_id)
    
    parcels = query.all()
    
    return [
        ParcelResponse(
            id=parcel.id,
            auctionId=parcel.auction_id or "",
            apn=parcel.apn or "",
            address=parcel.address or "",
            county=parcel.county or "",
            state=parcel.state or "",
            acreage=float(parcel.acreage) if parcel.acreage else 0.0,
            marketValue=float(parcel.market_value) if parcel.market_value else 0.0,
            minBid=float(parcel.min_bid) if parcel.min_bid else 0.0,
            zoning=parcel.zoning or "",
            status=parcel.status,
            latitude=float(parcel.latitude) if parcel.latitude else 0.0,
            longitude=float(parcel.longitude) if parcel.longitude else 0.0,
            taxes=float(parcel.taxes) if parcel.taxes else None,
            assessedValue=float(parcel.assessed_value) if parcel.assessed_value else (float(parcel.market_value) if parcel.market_value else None),
            floodFlag=parcel.flood_flag if parcel.flood_flag is not None else None,
            lastUpdatedAt=parcel.last_updated_at.isoformat() if parcel.last_updated_at else None
        )
        for parcel in parcels
    ]


@router.get("/parcels/{parcel_id}/comps", response_model=List[ComparableSaleResponse])
async def get_parcel_comps(
    parcel_id: str,
    window: str = Query("6m", regex="^(6m|12m)$", description="Time window: 6m or 12m"),
    db: Session = Depends(get_db)
):
    """
    Get comparable sales for a parcel within the specified time window.
    
    Args:
        parcel_id: Parcel ID
        window: Time window - "6m" for 6 months or "12m" for 12 months
        
    Returns:
        List of comparable sales sorted by similarity score (descending)
    """
    # Get the parcel - try by ID first, then by APN
    parcel = db.query(Parcel).filter(Parcel.id == parcel_id).first()
    if not parcel:
        # Try by APN if parcel_id is actually an APN
        parcel = db.query(Parcel).filter(Parcel.apn == parcel_id).first()
    
    if not parcel:
        raise HTTPException(status_code=404, detail="Parcel not found")
    
    # Use APN for matching comparable sales
    parcel_id_norm = parcel.apn or parcel.id
    
    # Calculate date threshold
    months = 6 if window == "6m" else 12
    threshold_date = date.today() - timedelta(days=months * 30)
    
    # Get comparable sales
    comps = db.query(ComparableSale).filter(
        ComparableSale.parcel_id_norm == parcel_id_norm,
        ComparableSale.sold_date >= threshold_date
    ).order_by(ComparableSale.similarity_score.desc()).all()
    
    # If no comps found, return empty list (enrichment pipeline can populate later)
    return [
        ComparableSaleResponse(
            address=comp.address or "Address not available",
            area=f"{float(comp.acreage):.1f} ac" if comp.acreage else "N/A",
            price=float(comp.sold_price),
            date=comp.sold_date.isoformat(),
            distance=f"{float(comp.distance):.1f} mi" if comp.distance else "N/A",
            similarity=int(round(float(comp.similarity_score)))
        )
        for comp in comps
    ]
