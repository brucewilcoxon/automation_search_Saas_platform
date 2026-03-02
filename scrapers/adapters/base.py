"""
Base adapter class for county-specific scrapers.
"""
from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from datetime import date


class BaseCountyAdapter(ABC):
    """
    Base class for county-specific auction data adapters.
    
    Each county adapter should inherit from this class and implement
    the abstract methods to scrape auction data from county-specific sources.
    """
    
    def __init__(self, county_id: str, source_url: str):
        """
        Initialize the adapter.
        
        Args:
            county_id: County identifier
            source_url: Base URL for the auction source
        """
        self.county_id = county_id
        self.source_url = source_url
    
    @abstractmethod
    def discover_auction_events(self) -> List[Dict[str, Any]]:
        """
        Discover all available auction events from the county source.
        
        Returns:
            List of auction event dictionaries with keys:
            - event_id: Unique identifier for the event
            - event_date: Date of the auction
            - event_url: URL to the event page
            - status: Event status (upcoming, live, ended)
            - raw_json: Optional raw JSON snapshot of the event data
        """
        pass
    
    @abstractmethod
    def list_auction_items(self, event_url: str) -> List[Dict[str, Any]]:
        """
        List all auction items for a specific event.
        
        Args:
            event_url: URL to the auction event page
            
        Returns:
            List of auction item dictionaries with keys:
            - item_id: Unique identifier for the item
            - parcel_id_raw: Raw parcel ID from source
            - opening_bid: Opening bid amount
            - status: Item status (available, sold, cancelled, pending)
            - item_url: URL to the item detail page
            - raw_json: Optional raw JSON snapshot of the item data
        """
        pass
    
    def parse_item_detail(self, item_url: str) -> Optional[Dict[str, Any]]:
        """
        Parse detailed information for a specific auction item.
        Optional for Milestone 2.
        
        Args:
            item_url: URL to the item detail page
            
        Returns:
            Dictionary with detailed item information or None
        """
        return None
    
    def normalize_parcel_id(self, raw_parcel_id: str) -> str:
        """
        Normalize a parcel ID by removing special characters.
        
        Args:
            raw_parcel_id: Raw parcel ID from source
            
        Returns:
            Normalized parcel ID
        """
        return "".join(c for c in raw_parcel_id if c.isalnum())
