"""
Letter tool endpoints.
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
from pydantic import BaseModel
from datetime import datetime
from backend.app.core.database import get_db
from backend.db.models.letter_template import LetterTemplate
from backend.db.models.letter_campaign import LetterCampaign
from backend.db.models.letter import Letter
from backend.db.models.parcel import Parcel
from backend.app.schemas.letters import (
    LetterTemplateRequest,
    LetterTemplateResponse,
    LetterCampaignRequest,
    LetterCampaignResponse,
    LetterResponse
)
from backend.app.core.email_provider import EmailProvider

router = APIRouter()


@router.post("/letters/templates", response_model=LetterTemplateResponse)
async def create_letter_template(
    request: LetterTemplateRequest,
    db: Session = Depends(get_db)
):
    """
    Create a new letter template.
    """
    template_id = f"template-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}-{request.name.lower().replace(' ', '-')}"
    
    template = LetterTemplate(
        id=template_id,
        name=request.name,
        subject=request.subject,
        body=request.body,
        merge_fields=request.merge_fields
    )
    
    db.add(template)
    db.commit()
    db.refresh(template)
    
    return LetterTemplateResponse(
        id=template.id,
        name=template.name,
        subject=template.subject,
        body=template.body,
        mergeFields=template.merge_fields or {},
        createdAt=template.created_at.isoformat(),
        updatedAt=template.updated_at.isoformat() if template.updated_at else None
    )


@router.get("/letters/templates", response_model=List[LetterTemplateResponse])
async def get_letter_templates(
    db: Session = Depends(get_db)
):
    """
    Get all letter templates.
    """
    templates = db.query(LetterTemplate).order_by(LetterTemplate.created_at.desc()).all()
    
    return [
        LetterTemplateResponse(
            id=template.id,
            name=template.name,
            subject=template.subject,
            body=template.body,
            mergeFields=template.merge_fields or {},
            createdAt=template.created_at.isoformat(),
            updatedAt=template.updated_at.isoformat() if template.updated_at else None
        )
        for template in templates
    ]


@router.post("/letters/campaigns", response_model=LetterCampaignResponse)
async def create_letter_campaign(
    request: LetterCampaignRequest,
    db: Session = Depends(get_db)
):
    """
    Create a new letter campaign.
    """
    # Verify template exists
    template = db.query(LetterTemplate).filter(LetterTemplate.id == request.template_id).first()
    if not template:
        raise HTTPException(status_code=404, detail="Template not found")
    
    # Verify parcels exist
    parcels = db.query(Parcel).filter(Parcel.id.in_(request.parcel_ids)).all()
    if len(parcels) != len(request.parcel_ids):
        raise HTTPException(status_code=404, detail="One or more parcels not found")
    
    campaign_id = f"campaign-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}"
    
    # Create campaign
    campaign = LetterCampaign(
        id=campaign_id,
        template_id=request.template_id,
        parcel_ids=request.parcel_ids,
        merge_fields=request.merge_fields,
        status="draft",
        total_letters=len(request.parcel_ids)
    )
    
    db.add(campaign)
    db.flush()
    
    # Create individual letters for each parcel
    for parcel in parcels:
        # Render letter body with merge fields
        body = template.body
        subject = template.subject or ""
        
        # Default merge fields from parcel
        default_fields = {
            "parcel_id": parcel.id,
            "apn": parcel.apn or "",
            "address": parcel.address or "",
            "county": parcel.county or "",
            "state": parcel.state or "",
            "acreage": str(parcel.acreage) if parcel.acreage else "",
            "zoning": parcel.zoning or "",
            "market_value": str(parcel.market_value) if parcel.market_value else "",
            "min_bid": str(parcel.min_bid) if parcel.min_bid else "",
        }
        
        # Merge with campaign-specific fields
        merge_data = {**default_fields, **(request.merge_fields or {})}
        
        # Replace merge fields in template (simple {{field}} replacement)
        for key, value in merge_data.items():
            body = body.replace(f"{{{{{key}}}}}", str(value))
            subject = subject.replace(f"{{{{{key}}}}}", str(value))
        
        letter = Letter(
            id=f"letter-{campaign.id}-{parcel.id}",
            campaign_id=campaign.id,
            parcel_id=parcel.id,
            subject=subject,
            body=body,
            status="pending",
            raw_json={
                "merge_fields": merge_data,
                "parcel_data": {
                    "apn": parcel.apn,
                    "address": parcel.address,
                    "county": parcel.county,
                    "state": parcel.state
                }
            }
        )
        db.add(letter)
    
    db.commit()
    db.refresh(campaign)
    
    return LetterCampaignResponse(
        id=campaign.id,
        templateId=campaign.template_id,
        parcelIds=campaign.parcel_ids,
        mergeFields=campaign.merge_fields or {},
        status=campaign.status,
        totalLetters=campaign.total_letters,
        sentCount=campaign.sent_count,
        failedCount=campaign.failed_count,
        createdAt=campaign.created_at.isoformat(),
        updatedAt=campaign.updated_at.isoformat() if campaign.updated_at else None
    )


@router.get("/letters/campaigns/{campaign_id}", response_model=LetterCampaignResponse)
async def get_letter_campaign(
    campaign_id: str,
    db: Session = Depends(get_db)
):
    """
    Get a letter campaign by ID.
    """
    campaign = db.query(LetterCampaign).filter(LetterCampaign.id == campaign_id).first()
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")
    
    return LetterCampaignResponse(
        id=campaign.id,
        templateId=campaign.template_id,
        parcelIds=campaign.parcel_ids,
        mergeFields=campaign.merge_fields or {},
        status=campaign.status,
        totalLetters=campaign.total_letters,
        sentCount=campaign.sent_count,
        failedCount=campaign.failed_count,
        createdAt=campaign.created_at.isoformat(),
        updatedAt=campaign.updated_at.isoformat() if campaign.updated_at else None
    )


@router.post("/letters/{letter_id}/send")
async def send_letter(
    letter_id: str,
    db: Session = Depends(get_db)
):
    """
    Send a letter (stub implementation with logging).
    In production, this would integrate with an email provider.
    """
    letter = db.query(Letter).filter(Letter.id == letter_id).first()
    if not letter:
        raise HTTPException(status_code=404, detail="Letter not found")
    
    if letter.status == "sent":
        raise HTTPException(status_code=400, detail="Letter already sent")
    
    # Get email provider (stub implementation)
    email_provider = EmailProvider()
    
    try:
        # Attempt to send (stub - just logs for now)
        result = email_provider.send_email(
            to=letter.recipient_email or "placeholder@example.com",
            subject=letter.subject or "Letter",
            body=letter.body
        )
        
        # Update letter status
        letter.status = "sent"
        letter.sent_at = datetime.utcnow()
        letter.raw_json = letter.raw_json or {}
        letter.raw_json["send_result"] = result
        
        # Update campaign stats
        campaign = letter.campaign
        campaign.sent_count += 1
        if campaign.sent_count == campaign.total_letters:
            campaign.status = "completed"
        
        db.commit()
        
        return {
            "status": "success",
            "letter_id": letter.id,
            "sent_at": letter.sent_at.isoformat(),
            "message": "Letter sent successfully (stub - logged only)"
        }
        
    except Exception as e:
        # Update letter status to failed
        letter.status = "failed"
        letter.error_message = str(e)
        
        # Update campaign stats
        campaign = letter.campaign
        campaign.failed_count += 1
        campaign.status = "failed"
        
        db.commit()
        
        raise HTTPException(status_code=500, detail=f"Failed to send letter: {str(e)}")
