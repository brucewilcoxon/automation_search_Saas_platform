"""
Pydantic schemas for letter tool endpoints.
"""
from pydantic import BaseModel
from typing import List, Optional, Dict, Any


class LetterTemplateRequest(BaseModel):
    """Request schema for creating a letter template."""
    name: str
    subject: Optional[str] = None
    body: str
    merge_fields: Optional[Dict[str, Any]] = None


class LetterTemplateResponse(BaseModel):
    """Response schema for letter template."""
    id: str
    name: str
    subject: Optional[str]
    body: str
    mergeFields: Dict[str, Any]
    createdAt: str
    updatedAt: Optional[str]
    
    class Config:
        from_attributes = True


class LetterCampaignRequest(BaseModel):
    """Request schema for creating a letter campaign."""
    parcel_ids: List[str]
    template_id: str
    merge_fields: Optional[Dict[str, Any]] = None


class LetterCampaignResponse(BaseModel):
    """Response schema for letter campaign."""
    id: str
    templateId: str
    parcelIds: List[str]
    mergeFields: Dict[str, Any]
    status: str
    totalLetters: int
    sentCount: int
    failedCount: int
    createdAt: str
    updatedAt: Optional[str]
    
    class Config:
        from_attributes = True


class LetterResponse(BaseModel):
    """Response schema for individual letter."""
    id: str
    campaignId: str
    parcelId: Optional[str]
    subject: Optional[str]
    body: str
    status: str
    sentAt: Optional[str]
    errorMessage: Optional[str]
    createdAt: str
    
    class Config:
        from_attributes = True
