"""
Letter template model.
"""
from sqlalchemy import Column, String, Text, DateTime, JSON
from sqlalchemy.sql import func
from backend.app.core.database import Base


class LetterTemplate(Base):
    """Letter template entity."""
    __tablename__ = "letter_templates"
    
    id = Column(String, primary_key=True, index=True)
    name = Column(String, nullable=False)
    subject = Column(String, nullable=True)
    body = Column(Text, nullable=False)  # Template body with merge fields
    merge_fields = Column(JSON, nullable=True)  # Available merge fields definition
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
