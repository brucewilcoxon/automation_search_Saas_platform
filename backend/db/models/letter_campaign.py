"""
Letter campaign model.
"""
from sqlalchemy import Column, String, ForeignKey, DateTime, JSON, Integer
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from backend.app.core.database import Base


class LetterCampaign(Base):
    """Letter campaign entity."""
    __tablename__ = "letter_campaigns"
    
    id = Column(String, primary_key=True, index=True)
    template_id = Column(String, ForeignKey("letter_templates.id"), nullable=False)
    parcel_ids = Column(JSON, nullable=False)  # Array of parcel IDs
    merge_fields = Column(JSON, nullable=True)  # Campaign-specific merge field values
    status = Column(String, nullable=False, default="draft")  # draft, sending, completed, failed
    total_letters = Column(Integer, nullable=False, default=0)
    sent_count = Column(Integer, nullable=False, default=0)
    failed_count = Column(Integer, nullable=False, default=0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    template = relationship("LetterTemplate")
    letters = relationship("Letter", back_populates="campaign", cascade="all, delete-orphan")
