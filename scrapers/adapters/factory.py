"""
Factory for creating county adapters.
"""
from typing import Optional
from scrapers.adapters.base import BaseCountyAdapter
from scrapers.adapters.miami_dade import MiamiDadeAdapter


def create_adapter(state: str, county: str) -> Optional[BaseCountyAdapter]:
    """
    Create an adapter instance for the given state and county.
    
    Args:
        state: State code (e.g., 'FL')
        county: County name (e.g., 'Miami-Dade')
        
    Returns:
        Adapter instance or None if not supported
    """
    state_upper = state.upper()
    county_lower = county.lower().strip()
    
    # Florida counties
    if state_upper == 'FL':
        if county_lower in ['miami-dade', 'miamidade', 'miami dade']:
            return MiamiDadeAdapter()
        # Add more Florida counties here as they're implemented
        # elif county_lower in ['broward', 'broward county']:
        #     return BrowardAdapter()
    
    return None
