from sqlalchemy import Boolean, Column, Integer, String, Text, text

from app.database.base_class import Base


class FooterSetting(Base):
    __tablename__ = "footer_settings"

    id = Column(Integer, primary_key=True)
    brand_name = Column(String(255), nullable=False)
    brand_highlight = Column(String(255), nullable=True)
    contact_heading = Column(String(100), nullable=False, server_default="Contact Us")
    whatsapp_label = Column(String(100), nullable=False, server_default="WhatsApp")
    whatsapp_number = Column(String(40), nullable=False)
    phone_label = Column(String(100), nullable=False, server_default="Call Us")
    phone_number = Column(String(40), nullable=False)
    email = Column(String(255), nullable=True)
    connect_label = Column(String(100), nullable=False)
    connect_url = Column(String(500), nullable=False)
    store_label = Column(String(100), nullable=False)
    store_url = Column(String(500), nullable=False)
    app_heading = Column(String(100), nullable=False, server_default="Download App")
    app_store_url = Column(String(500), nullable=True)
    app_store_badge = Column(String(500), nullable=True)
    play_store_url = Column(String(500), nullable=True)
    play_store_badge = Column(String(500), nullable=True)
    copyright_text = Column(String(500), nullable=False)
    is_active = Column(Boolean, nullable=False, server_default=text("1"))


class FooterLink(Base):
    __tablename__ = "footer_links"

    id = Column(Integer, primary_key=True)
    section = Column(String(50), nullable=False, index=True)
    label = Column(String(255), nullable=False)
    slug = Column(String(255), nullable=True, unique=True, index=True)
    url = Column(String(500), nullable=False)
    content = Column(Text, nullable=True)
    sort_order = Column(Integer, nullable=False, server_default="0")
    is_active = Column(Boolean, nullable=False, server_default=text("1"))
