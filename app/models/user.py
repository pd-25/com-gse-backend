from datetime import datetime
from app.database.base_class import Base
from sqlalchemy import Boolean, Column, DateTime, Integer, String, Text, ForeignKey, text
from sqlalchemy.orm import relationship


class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    phone = Column(String(20), unique=True, index=True, nullable=True)
    password = Column(String(255), nullable=False)
    avatar = Column(Text, nullable=True)
    is_active = Column(Boolean, default=True, server_default='1')
    is_verified = Column(Boolean, default=False, server_default='0')
    created_at = Column(DateTime, default=datetime.now, server_default=text('CURRENT_TIMESTAMP'))
    updated_at = Column(DateTime, default=datetime.now, server_default=text('CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP'))
    deleted_at = Column(DateTime, nullable=True)

    # Relationships
    addresses = relationship("UserAddress", back_populates="user", cascade="all, delete-orphan")
