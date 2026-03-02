"""
Miami-Dade County adapter for RealTaxDeed platform.
"""
from typing import List, Dict, Any
from scrapers.adapters.realtaxdeed_base import RealTaxDeedBaseAdapter


class MiamiDadeAdapter(RealTaxDeedBaseAdapter):
    """
    Miami-Dade County auction adapter.
    Uses RealTaxDeed platform at https://miamidade.realforeclose.com
    """
    
    def __init__(self):
        super().__init__(
            county_id="miami-dade",
            source_url="https://miamidade.realforeclose.com",
            county_name="Miami-Dade"
        )
    
    def discover_auction_events(self) -> List[Dict[str, Any]]:
        """
        Discover auction events for Miami-Dade County.
        Override base implementation if county-specific logic is needed.
        """
        return super().discover_auction_events()
    
    def list_auction_items(self, event_url: str) -> List[Dict[str, Any]]:
        """
        List auction items for Miami-Dade County.
        Override base implementation if county-specific logic is needed.
        """
        return super().list_auction_items(event_url)
    
    def normalize_parcel_id(self, raw_parcel_id: str) -> str:
        """
        Miami-Dade uses format: 30-2104-001-0010
        Normalized: 30210400010010
        """
        return super().normalize_parcel_id(raw_parcel_id)
