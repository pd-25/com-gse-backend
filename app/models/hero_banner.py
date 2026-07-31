from datetime import datetime

from sqlalchemy import Boolean, Column, DateTime, Integer, Numeric, String, Text, text

from app.database.base_class import Base


class HeroBanner(Base):
    __tablename__ = "hero_banners"

    id = Column(Integer, primary_key=True)
    title = Column(String(255), nullable=False)
    subtitle = Column(String(255), nullable=True)
    price = Column(Numeric(10, 2), nullable=True)
    currency = Column(String(3), nullable=False, default="USD", server_default="USD")
    image = Column(Text, nullable=False)
    button_text = Column(String(100), nullable=False, default="Explore Shop", server_default="Explore Shop")
    button_url = Column(String(500), nullable=False, default="/products", server_default="/products")
    display_order = Column(Integer, nullable=False, default=0, server_default="0")
    is_active = Column(Boolean, nullable=False, default=True, server_default="1")
    created_at = Column(DateTime, default=datetime.now, server_default=text("CURRENT_TIMESTAMP"))
    updated_at = Column(
        DateTime,
        default=datetime.now,
        server_default=text("CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP"),
    )
    deleted_at = Column(DateTime, nullable=True)
