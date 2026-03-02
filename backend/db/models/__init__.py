"""
SQLAlchemy models for all database entities.
Import all models here to ensure they're registered with SQLAlchemy.
"""
# Import order matters for relationships
from backend.db.models.county import County
from backend.db.models.auction_source import AuctionSource
from backend.db.models.auction_event import AuctionEvent
from backend.db.models.auction_item import AuctionItem
from backend.db.models.parcel import Parcel
from backend.db.models.ingest_run import IngestRun
from backend.db.models.comparable_sale import ComparableSale
from backend.db.models.cash_buyer import CashBuyer
from backend.db.models.letter_template import LetterTemplate
from backend.db.models.letter_campaign import LetterCampaign
from backend.db.models.letter import Letter
from backend.db.models.report import Report

__all__ = [
    "County",
    "AuctionSource",
    "AuctionEvent",
    "AuctionItem",
    "Parcel",
    "IngestRun",
    "ComparableSale",
    "CashBuyer",
    "LetterTemplate",
    "LetterCampaign",
    "Letter",
    "Report",
]
