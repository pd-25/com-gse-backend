from app.database.base_class import Base
from datetime import datetime
from sqlalchemy import Column, Integer, Text, String, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship
class Categories(Base):
    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False)
    slug = Column(String(255),unique=True, index=True, nullable=False)
    description = Column(Text, nullable=True)
    image = Column(Text, nullable=True)
    parent_id = Column(Integer, ForeignKey("categories.id"), nullable=True)
    # Self-referencing relationship
    parent = relationship(
        "Categories",
        remote_side=[id],
        backref="children"
    )
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now)
    deleted_at = Column(DateTime, nullable=True)
    is_active = Column(Boolean, default=False)
    