"""
FastAPI main application entry point.
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.app.api import health, auctions, auction_items, parcels, ingest, cash_buyers, letters, reports
from backend.app.core.config import settings
from backend.app.core.logging_config import configure_logging

# Configure structured logging
configure_logging()

app = FastAPI(
    title="Auction Navigator API",
    description="Backend API for auction navigator suite",
    version="1.0.0",
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
)

# Include routers
app.include_router(health.router, tags=["health"])
app.include_router(auctions.router, prefix="/api", tags=["auctions"])
app.include_router(auction_items.router, prefix="/api", tags=["auction-items"])
app.include_router(parcels.router, prefix="/api", tags=["parcels"])
app.include_router(ingest.router, prefix="/api", tags=["ingest"])
app.include_router(cash_buyers.router, prefix="/api", tags=["cash-buyers"])
app.include_router(letters.router, prefix="/api", tags=["letters"])
app.include_router(reports.router, prefix="/api", tags=["reports"])
