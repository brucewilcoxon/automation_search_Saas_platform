"""
County adapter framework for scraping auction data.
"""
from scrapers.adapters.base import BaseCountyAdapter
from scrapers.adapters.factory import create_adapter

__all__ = ["BaseCountyAdapter", "create_adapter"]
