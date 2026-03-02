"""
Letter model.
"""
from sqlalchemy import Column, String, ForeignKey, DateTime, Text, JSON, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from backend.app.core.database import Base


class Letter(Base):
    """Letter entity (individual letter in a campaign)."""
    __tablename__ = "letters"
    
    id = Column(String, primary_key=True, index=True)
    campaign_id = Column(String, ForeignKey("letter_campaigns.id"), nullable=False, index=True)
    parcel_id = Column(String, nullable=True, index=True)
    recipient_name = Column(String, nullable=True)
    recipient_email = Column(String, nullable=True)
    recipient_address = Column(String, nullable=True)
    subject = Column(String, nullable=True)
    body = Column(Text, nullable=False)  # Rendered letter body
    status = Column(String, nullable=False, default="pending")  # pending, sent, failed
    sent_at = Column(DateTime(timezone=True), nullable=True)
    error_message = Column(String, nullable=True)
    raw_json = Column(JSON, nullable=True)  # Additional metadata
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    campaign = relationship("LetterCampaign", back_populates="letters")
