"""
Parcel enrichment pipeline structure.
Placeholder implementations for data enrichment sources.
"""
from typing import Dict, Any, Optional
from sqlalchemy.orm import Session
from backend.db.models.parcel import Parcel
from backend.app.core.comps import calculate_distance_miles, calculate_similarity_score


class EnrichmentPipeline:
    """
    Pipeline for enriching parcel data from various sources.
    """
    
    def __init__(self, db: Session):
        self.db = db
    
    def enrich_parcel(self, parcel: Parcel) -> Dict[str, Any]:
        """
        Enrich a parcel with data from all available sources.
        
        Returns:
            Dictionary with enrichment results
        """
        results = {
            "taxes": self.enrich_taxes(parcel),
            "assessed_value": self.enrich_assessed_value(parcel),
            "flood_flag": self.enrich_flood_zone(parcel),
            "comparable_sales": self.enrich_comparable_sales(parcel)
        }
        return results
    
    def enrich_taxes(self, parcel: Parcel) -> Optional[float]:
        """
        Enrich tax data for a parcel.
        Placeholder - implement actual tax data source integration.
        """
        # TODO: Integrate with county tax assessor API or scraping
        # For now, return None (data pending)
        return None
    
    def enrich_assessed_value(self, parcel: Parcel) -> Optional[float]:
        """
        Enrich assessed value for a parcel.
        Placeholder - implement actual assessor data integration.
        """
        # TODO: Integrate with county assessor API
        # For now, use market_value if available
        if parcel.market_value:
            return float(parcel.market_value)
        return None
    
    def enrich_flood_zone(self, parcel: Parcel) -> Optional[bool]:
        """
        Enrich flood zone flag for a parcel.
        Placeholder - implement FEMA flood zone lookup.
        """
        # TODO: Integrate with FEMA flood zone API
        # For now, return None (data pending)
        return None
    
    def enrich_comparable_sales(self, parcel: Parcel) -> int:
        """
        Enrich comparable sales for a parcel.
        Placeholder - implement actual comps data source.
        
        Returns:
            Number of comparable sales found/created
        """
        # TODO: Integrate with MLS, county recorder, or other sales data source
        # For now, return 0 (no comps found)
        return 0


def create_comparable_sale(
    db: Session,
    parcel: Parcel,
    comp_address: str,
    comp_acreage: float,
    comp_price: float,
    comp_date: str,
    comp_zoning: Optional[str] = None,
    comp_lat: Optional[float] = None,
    comp_lng: Optional[float] = None
) -> Optional[str]:
    """
    Create a comparable sale record for a parcel.
    Calculates distance and similarity score automatically.
    
    Args:
        db: Database session
        parcel: Target parcel
        comp_address: Comparable sale address
        comp_acreage: Comparable sale acreage
        comp_price: Comparable sale price
        comp_date: Comparable sale date (ISO format)
        comp_zoning: Comparable sale zoning (optional)
        comp_lat: Comparable sale latitude (optional)
        comp_lng: Comparable sale longitude (optional)
        
    Returns:
        Comparable sale ID if created, None otherwise
    """
    from datetime import datetime
    from backend.db.models.comparable_sale import ComparableSale
    
    # Parse date
    try:
        sold_date = datetime.fromisoformat(comp_date).date()
    except (ValueError, AttributeError):
        return None
    
    # Calculate distance if coordinates available
    distance_miles = None
    if parcel.latitude and parcel.longitude and comp_lat and comp_lng:
        distance_miles = calculate_distance_miles(
            float(parcel.latitude),
            float(parcel.longitude),
            comp_lat,
            comp_lng
        )
    
    # Calculate similarity score
    similarity_score = calculate_similarity_score(
        target_acreage=float(parcel.acreage) if parcel.acreage else None,
        target_zoning=parcel.zoning,
        target_lat=float(parcel.latitude) if parcel.latitude else None,
        target_lng=float(parcel.longitude) if parcel.longitude else None,
        comp_acreage=comp_acreage,
        comp_zoning=comp_zoning,
        comp_lat=comp_lat,
        comp_lng=comp_lng,
        distance_miles=distance_miles
    )
    
    # Generate comp ID
    comp_id = f"comp-{parcel.apn}-{sold_date.isoformat()}-{int(comp_price)}"
    
    # Check if already exists
    existing = db.query(ComparableSale).filter(ComparableSale.comp_id == comp_id).first()
    if existing:
        return existing.id
    
    # Create new comparable sale
    comp_sale = ComparableSale(
        id=f"comp-{parcel.id}-{sold_date.isoformat()}-{int(comp_price)}",
        parcel_id_norm=parcel.apn or parcel.id,
        comp_id=comp_id,
        sold_date=sold_date,
        sold_price=comp_price,
        distance=distance_miles,
        similarity_score=similarity_score,
        address=comp_address,
        acreage=comp_acreage,
        zoning=comp_zoning,
        raw_json={
            "source": "enrichment_pipeline",
            "created_at": datetime.utcnow().isoformat()
        }
    )
    
    db.add(comp_sale)
    db.commit()
    db.refresh(comp_sale)
    
    return comp_sale.id
