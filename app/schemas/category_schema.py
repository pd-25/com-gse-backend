from datetime import datetime
from typing import Optional

from pydantic import BaseModel

class CategorySchema(BaseModel):
    id: int
    slug: str
    created_at: Optional[datetime] = None
    
    
class CategoryFilterSchema(BaseModel):
    limit: Optional[int] = 30
    
class CategoryListResponse(CategorySchema):
    name: str
    image: Optional[str] = None
    thumbnail_image: Optional[str] = None
    total_products: int = 0


class CategoryDetailInfo(BaseModel):
    id: int
    slug: str
    name: str
    description: Optional[str] = None
    quality_standards: Optional[str] = None
    buying_guide: Optional[str] = None
    image: Optional[str] = None
    thumbnail_image: Optional[str] = None


class SubcategoryResponse(CategoryDetailInfo):
    total_products: int = 0
    min_price: Optional[float] = None
    max_price: Optional[float] = None


class CategoryProductResponse(BaseModel):
    id: int
    slug: str
    title: str
    brand: Optional[str] = None
    description: Optional[str] = None
    short_desc: Optional[str] = None
    currency: str = "USD"
    price: float
    old_price: Optional[float] = None
    rating: Optional[float] = None
    sold_count: int = 0
    badge: Optional[str] = None
    image: str
    subcategory_id: Optional[int] = None
    subcategory_slug: Optional[str] = None
    subcategory_name: Optional[str] = None


class CategoryPriceSummary(BaseModel):
    currency: str = "USD"
    min_price: Optional[float] = None
    max_price: Optional[float] = None
    average_rating: Optional[float] = None
    total_products: int = 0


class CategoryDetailResponse(BaseModel):
    category: CategoryDetailInfo
    subcategories: list[SubcategoryResponse]
    products: list[CategoryProductResponse]
    summary: CategoryPriceSummary
