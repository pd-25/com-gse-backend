from datetime import datetime

from sqlalchemy import Boolean, Column, DateTime, Integer, String, Text, text

from app.database.base_class import Base


class HomepageSection(Base):
    __tablename__ = "homepage_sections"

    id = Column(Integer, primary_key=True)
    section_key = Column(String(100), unique=True, index=True, nullable=False)
    title = Column(String(255), nullable=False)
    subtitle = Column(Text, nullable=True)
    display_order = Column(Integer, nullable=False, default=0, server_default="0")
    is_active = Column(Boolean, nullable=False, default=True, server_default="1")
    created_at = Column(DateTime, default=datetime.now, server_default=text("CURRENT_TIMESTAMP"))
    updated_at = Column(
        DateTime,
        default=datetime.now,
        server_default=text("CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP"),
    )
    deleted_at = Column(DateTime, nullable=True)
