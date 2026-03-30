"""
Content plan model for weekly strategy output.
"""

from datetime import date, datetime

from sqlalchemy import JSON, Column, Date, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship

from app.database import Base


class ContentPlan(Base):
    """Stores one generated weekly plan for a founder."""

    __tablename__ = "content_plans"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    product_idea_id = Column(
        Integer, ForeignKey("product_ideas.id", ondelete="CASCADE"), nullable=False, index=True
    )
    brand_profile_id = Column(
        Integer, ForeignKey("brand_profiles.id", ondelete="SET NULL"), nullable=True, index=True
    )
    week_start = Column(Date, default=date.today, nullable=False)
    platforms = Column(JSON, default=list, nullable=False)
    weekly_themes = Column(JSON, default=list, nullable=False)
    plan_notes = Column(Text, nullable=True)
    status = Column(String(50), default="draft", nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    owner = relationship("User", backref="content_plans")
    product_idea = relationship("ProductIdea", backref="content_plans")
    brand_profile = relationship("BrandProfile", backref="content_plans")

    def __repr__(self):
        return f"<ContentPlan(id={self.id}, user_id={self.user_id}, status={self.status})>"
