from datetime import datetime
from app.database.base_class import Base
from sqlalchemy import Boolean, Column, DateTime, Integer, Numeric, String, Text, ForeignKey, text
from sqlalchemy.orm import relationship


class Product(Base):
    __tablename__ = 'products'

    id = Column(Integer, primary_key=True)
    slug = Column(String(255), unique=True, index=True, nullable=False)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    short_desc = Column(Text, nullable=True)
    currency = Column(String(10), nullable=True)
    price = Column(Numeric(10, 2), nullable=True)
    price_per_measurement = Column(String(50), nullable=True)
    min_order = Column(Integer, nullable=True)
    country_id = Column(Integer, ForeignKey("countries.id"), nullable=True)
    supplier_id = Column(Integer, ForeignKey("suppliers.id"), nullable=True)
    product_type_id = Column(Integer, ForeignKey("product_types.id"), nullable=True)
    category_id = Column(Integer, ForeignKey("categories.id"), nullable=True)
    id_recomended = Column(Boolean, default=False, server_default="0")
    created_at = Column(DateTime, default=datetime.now, server_default=text('CURRENT_TIMESTAMP'))
    updated_at = Column(DateTime, default=datetime.now, server_default=text('CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP  '))
    deleted_at = Column(DateTime, nullable=True)

    # Relationships
    country = relationship("Country", backref="products")
    supplier = relationship("Supplier", backref="products")
    product_type = relationship("ProductType", backref="products")
    category = relationship("Categories", backref="products")
    images = relationship("ProductImage", back_populates="product", cascade="all, delete-orphan")
    views = relationship("ProductView", back_populates="product", cascade="all, delete-orphan")
    primary_image = relationship(
        "ProductImage",
        primaryjoin="and_(Product.id==ProductImage.product_id)",
        order_by="ProductImage.id",
        uselist=False,
        viewonly=True
    )

