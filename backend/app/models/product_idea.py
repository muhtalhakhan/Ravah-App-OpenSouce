"""
Product idea model for founder onboarding context.
"""

from datetime import datetime

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship

from app.database import Base


class ProductIdea(Base):
    """Stores a founder's product concept and positioning context."""

    __tablename__ = "product_ideas"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    product_name = Column(String(200), nullable=False, index=True)
    short_description = Column(Text, nullable=False)
    problem_statement = Column(Text, nullable=True)
    target_audience = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    owner = relationship("User", backref="product_ideas")

    def __repr__(self):
        return f"<ProductIdea(id={self.id}, user_id={self.user_id}, product_name={self.product_name})>"
