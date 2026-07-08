from datetime import datetime
from app.database.base_class import Base
from sqlalchemy import Boolean, Column, DateTime, Integer, String, ForeignKey, text
from sqlalchemy.orm import relationship


class UserAddress(Base):
    __tablename__ = 'user_addresses'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    label = Column(String(50), nullable=True)  # e.g. "Home", "Office"
    full_name = Column(String(255), nullable=False)
    phone = Column(String(20), nullable=True)
    address_line_1 = Column(String(255), nullable=False)
    address_line_2 = Column(String(255), nullable=True)
    city = Column(String(100), nullable=False)
    state = Column(String(100), nullable=True)
    postal_code = Column(String(20), nullable=False)
    country = Column(String(100), nullable=False)
    is_default = Column(Boolean, default=False, server_default='0')
    created_at = Column(DateTime, default=datetime.now, server_default=text('CURRENT_TIMESTAMP'))
    updated_at = Column(DateTime, default=datetime.now, server_default=text('CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP'))
    deleted_at = Column(DateTime, nullable=True)

    # Relationships
    user = relationship("User", back_populates="addresses")
