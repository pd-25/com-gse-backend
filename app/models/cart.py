from datetime import datetime
from app.database.base_class import Base
from sqlalchemy import Column, DateTime, Integer, Numeric, String, Text, ForeignKey, text
from sqlalchemy.orm import relationship


class Cart(Base):
    __tablename__ = 'carts'

    id = Column(Integer, primary_key=True)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    quantity = Column(Integer, default=1, nullable=False)
    created_at = Column(DateTime, default=datetime.now, server_default=text('CURRENT_TIMESTAMP'))
    updated_at = Column(DateTime, default=datetime.now, server_default=text('CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP'))

    # Relationships
    product = relationship("Product", backref="carts")
    user = relationship("User", backref="carts")
    



