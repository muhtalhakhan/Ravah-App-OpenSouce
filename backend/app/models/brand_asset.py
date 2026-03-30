"""
Brand asset model for design identity and Figma metadata.
"""

from datetime import datetime

from sqlalchemy import JSON, Column, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from app.database import Base


class BrandAsset(Base):
    """Stores brand design inputs imported or entered by the founder."""

    __tablename__ = "brand_assets"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    brand_profile_id = Column(
        Integer, ForeignKey("brand_profiles.id", ondelete="SET NULL"), nullable=True, index=True
    )
    source_type = Column(String(50), default="manual", nullable=False)
    figma_file_url = Column(String(500), nullable=True)
    logo_url = Column(String(500), nullable=True)
    primary_color = Column(String(20), nullable=True)
    secondary_color = Column(String(20), nullable=True)
    typography = Column(String(200), nullable=True)
    metadata_json = Column(JSON, default=dict, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    owner = relationship("User", backref="brand_assets")
    brand_profile = relationship("BrandProfile", backref="assets")

    def __repr__(self):
        return f"<BrandAsset(id={self.id}, user_id={self.user_id}, source_type={self.source_type})>"
