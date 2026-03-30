"""
Content post model for per-platform generated post outputs.
"""

from datetime import datetime

from sqlalchemy import JSON, Column, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship

from app.database import Base


class ContentPost(Base):
    """Stores generated post variants tied to a weekly plan."""

    __tablename__ = "content_posts"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    content_plan_id = Column(
        Integer, ForeignKey("content_plans.id", ondelete="CASCADE"), nullable=False, index=True
    )
    platform = Column(String(40), nullable=False, index=True)
    day_index = Column(Integer, nullable=False)
    post_order = Column(Integer, default=0, nullable=False)
    hook = Column(String(280), nullable=True)
    caption = Column(Text, nullable=False)
    hashtags = Column(JSON, default=list, nullable=False)
    visual_prompt = Column(Text, nullable=True)
    status = Column(String(50), default="draft", nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    owner = relationship("User", backref="content_posts")
    content_plan = relationship("ContentPlan", backref="posts")

    def __repr__(self):
        return f"<ContentPost(id={self.id}, platform={self.platform}, day_index={self.day_index})>"
