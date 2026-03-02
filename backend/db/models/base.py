"""
Base model class for all database models.
"""
from sqlalchemy.ext.declarative import declarative_base
from backend.app.core.database import Base

__all__ = ["Base"]
