from datetime import datetime
from app.database.base_class import Base
from sqlalchemy import Boolean, Column, DateTime, Enum, Integer, Text, ForeignKey, text
from sqlalchemy.orm import relationship


class ProductImage(Base):
    __tablename__ = 'product_images'

    id = Column(Integer, primary_key=True)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    image = Column(Text, nullable=False, comment="Field name is image but it can have video also. type field will define")
    file_type = Column(Enum("image", "video", "motion", "gif"), nullable=True)
    is_preview = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.now, server_default=text('CURRENT_TIMESTAMP'))
    updated_at = Column(DateTime, default=datetime.now, server_default=text('CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP  '))

    # Relationships
    product = relationship("Product", back_populates="images")
