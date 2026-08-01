from app.database.base_class import Base
from datetime import datetime
from sqlalchemy import Column, Integer, Text, String, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship
class Categories(Base):
    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False)
    slug = Column(String(255),unique=True, index=True, nullable=False)
    description = Column(Text, nullable=True)
    quality_standards = Column(Text, nullable=True)
    buying_guide = Column(Text, nullable=True)
    image = Column(Text, nullable=True)
    thumbnail_image = Column(Text, nullable=True)
    showcase_image = Column(Text, nullable=True)
    showcase_tag = Column(String(100), nullable=True)
    showcase_description = Column(String(255), nullable=True)
    showcase_button_text = Column(String(100), nullable=True)
    showcase_button_url = Column(String(500), nullable=True)
    is_showcase = Column(Boolean, nullable=False, default=False, server_default="0")
    display_order = Column(Integer, nullable=False, default=0, server_default="0")
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
