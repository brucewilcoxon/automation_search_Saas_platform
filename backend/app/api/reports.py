"""
PDF report generation endpoints.
"""
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import Response
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional
from datetime import datetime
import os
import logging
from backend.app.core.database import get_db
from backend.db.models.parcel import Parcel
from backend.db.models.auction_event import AuctionEvent
from backend.db.models.comparable_sale import ComparableSale
from backend.db.models.report import Report
from backend.app.core.pdf_generator import PDFGenerator

router = APIRouter()
logger = logging.getLogger(__name__)


class AuctionPDFRequest(BaseModel):
    """Request model for generating auction PDF report."""
    parcel_id: Optional[str] = None
    event_id: Optional[str] = None


@router.post("/reports/auction-pdf")
async def generate_auction_pdf(
    request: AuctionPDFRequest,
    db: Session = Depends(get_db)
):
    """
    Generate a PDF report for an auction parcel or event.
    Returns the PDF file as a response.
    """
    if not request.parcel_id and not request.event_id:
        raise HTTPException(status_code=400, detail="Either parcel_id or event_id must be provided")
    
    # Get parcel data
    parcel = None
    if request.parcel_id:
        parcel = db.query(Parcel).filter(Parcel.id == request.parcel_id).first()
        if not parcel:
            raise HTTPException(status_code=404, detail="Parcel not found")
    
    # Get event data
    event = None
    if request.event_id:
        event = db.query(AuctionEvent).filter(AuctionEvent.id == request.event_id).first()
        if not event:
            raise HTTPException(status_code=404, detail="Event not found")
    
    # Get comparable sales if parcel available
    comps_6m = []
    comps_12m = []
    if parcel and parcel.apn:
        from datetime import date, timedelta
        threshold_6m = date.today() - timedelta(days=180)
        threshold_12m = date.today() - timedelta(days=365)
        
        comps_6m = db.query(ComparableSale).filter(
            ComparableSale.parcel_id_norm == parcel.apn,
            ComparableSale.sold_date >= threshold_6m
        ).order_by(ComparableSale.similarity_score.desc()).limit(10).all()
        
        comps_12m = db.query(ComparableSale).filter(
            ComparableSale.parcel_id_norm == parcel.apn,
            ComparableSale.sold_date >= threshold_12m
        ).order_by(ComparableSale.similarity_score.desc()).limit(10).all()
    
    # Generate PDF
    try:
        pdf_generator = PDFGenerator()
        pdf_bytes = pdf_generator.generate_auction_report(
            parcel=parcel,
            event=event,
            comps_6m=comps_6m,
            comps_12m=comps_12m
        )
        
        # Store report metadata
        report_id = f"report-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}"
        report = Report(
            id=report_id,
            report_type="auction_pdf",
            parcel_id=parcel.id if parcel else None,
            event_id=event.id if event else None,
            status="completed",
            file_size=len(pdf_bytes)
        )
        db.add(report)
        db.commit()
        
        logger.info(f"Generated PDF report {report_id} for parcel {request.parcel_id or 'N/A'}")
        
        return Response(
            content=pdf_bytes,
            media_type="application/pdf",
            headers={
                "Content-Disposition": f"attachment; filename=auction-report-{report_id}.pdf"
            }
        )
        
    except Exception as e:
        logger.error(f"Failed to generate PDF report: {str(e)}", exc_info=True)
        
        # Store failed report metadata
        report_id = f"report-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}"
        report = Report(
            id=report_id,
            report_type="auction_pdf",
            parcel_id=parcel.id if parcel else None,
            event_id=event.id if event else None,
            status="failed",
            error_message=str(e)
        )
        db.add(report)
        db.commit()
        
        raise HTTPException(status_code=500, detail=f"Failed to generate PDF: {str(e)}")
