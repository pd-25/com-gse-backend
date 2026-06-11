from datetime import datetime
from app.database.base_class import Base
from sqlalchemy import Boolean, Column, DateTime, Integer, Text, ForeignKey, text
from sqlalchemy.orm import relationship


class ProductView(Base):
    __tablename__ = 'product_views'

    id = Column(Integer, primary_key=True)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    client_ip_address = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.now, server_default=text('CURRENT_TIMESTAMP'))
    updated_at = Column(DateTime, default=datetime.now, server_default=text('CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP  '))

    # Relationships
    product = relationship("Product", back_populates="views")
