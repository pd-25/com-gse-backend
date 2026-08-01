from datetime import datetime
from app.database.base_class import Base
from sqlalchemy import Boolean, Column, DateTime, Integer, Numeric, String, Text, ForeignKey, text
from sqlalchemy.orm import relationship


class Product(Base):
    __tablename__ = 'products'

    id = Column(Integer, primary_key=True)
    slug = Column(String(255), unique=True, index=True, nullable=False)
    title = Column(String(255), nullable=False)
    brand = Column(String(150), nullable=True)
    description = Column(Text, nullable=True)
    short_desc = Column(Text, nullable=True)
    currency = Column(String(10), nullable=True)
    price = Column(Numeric(10, 2), nullable=True)
    old_price = Column(Numeric(10, 2), nullable=True)
    rating = Column(Numeric(2, 1), nullable=True)
    sold_count = Column(Integer, nullable=False, default=0, server_default="0")
    badge = Column(String(100), nullable=True)
    is_flash_sale = Column(Boolean, nullable=False, default=False, server_default="0")
    display_order = Column(Integer, nullable=False, default=0, server_default="0")
    price_per_measurement = Column(String(50), nullable=True)
    min_order = Column(Integer, nullable=True)
    # country_id = Column(Integer, ForeignKey("countries.id"), nullable=True)
    # supplier_id = Column(Integer, ForeignKey("suppliers.id"), nullable=True)
    product_type_id = Column(Integer, ForeignKey("product_types.id"), nullable=True)
    category_id = Column(Integer, ForeignKey("categories.id"), nullable=True)
    subcategory_id = Column(Integer, ForeignKey("categories.id"), nullable=True)
    id_recomended = Column(Boolean, default=False, server_default="0")
    created_at = Column(DateTime, default=datetime.now, server_default=text('CURRENT_TIMESTAMP'))
    updated_at = Column(DateTime, default=datetime.now, server_default=text('CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP  '))
    deleted_at = Column(DateTime, nullable=True)

    # Relationships
    # country = relationship("Country", backref="products")
    carts = relationship("Cart", back_populates="product", cascade="all, delete-orphan")
    product_type = relationship("ProductType", backref="products")
    category = relationship("Categories", foreign_keys=[category_id], backref="products")
    subcategory = relationship("Categories", foreign_keys=[subcategory_id], backref="subcategory_products")
    images = relationship("ProductImage", back_populates="product", cascade="all, delete-orphan")
    views = relationship("ProductView", back_populates="product", cascade="all, delete-orphan")
    primary_image = relationship(
        "ProductImage",
        primaryjoin="and_(Product.id==ProductImage.product_id)",
        order_by="ProductImage.id",
        uselist=False,
        viewonly=True
    )
