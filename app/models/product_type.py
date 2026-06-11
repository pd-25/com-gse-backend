from app.database.base_class import Base
from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, text


class ProductType(Base):
    __tablename__ = 'product_types'

    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False)
    created_at = Column(DateTime, default=datetime.now, server_default=text('CURRENT_TIMESTAMP'))
    updated_at = Column(DateTime, default=datetime.now, server_default=text('CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP  '))
    deleted_at = Column(DateTime, nullable=True)
