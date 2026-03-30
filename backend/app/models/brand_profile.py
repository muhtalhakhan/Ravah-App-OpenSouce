"""
Brand profile model capturing tone and voice inputs.
"""

from datetime import datetime

from sqlalchemy import JSON, Column, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship

from app.database import Base


class BrandProfile(Base):
    """Stores user-level brand voice profile used for generation."""

    __tablename__ = "brand_profiles"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
        index=True,
    )
    tone = Column(String(120), nullable=True)
    keywords = Column(JSON, default=list, nullable=False)
    sample_post = Column(Text, nullable=True)
    voice_guidelines = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    owner = relationship("User", backref="brand_profile")

    def __repr__(self):
        return f"<BrandProfile(id={self.id}, user_id={self.user_id}, tone={self.tone})>"
