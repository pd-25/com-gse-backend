from decimal import Decimal
from typing import List, Optional

from pydantic import BaseModel


class HomepageProductResponse(BaseModel):
    id: int
    slug: str
    title: str
    currency: str
    price: Decimal
    old_price: Optional[Decimal] = None
    rating: Optional[Decimal] = None
    sold_count: int
    badge: Optional[str] = None
    image: str


class FlashSaleFilterSchema(BaseModel):
    limit: int = 12


class CategoryShowcaseFilterSchema(BaseModel):
    limit: int = 2
    products_per_category: int = 8


class CategoryShowcaseResponse(BaseModel):
    id: int
    slug: str
    name: str
    tag: Optional[str] = None
    description: Optional[str] = None
    image: str
    button_text: str
    button_url: str
    total_products: int
    products: List[HomepageProductResponse]


class FlashSaleSectionResponse(BaseModel):
    key: str
    title: str
    subtitle: Optional[str] = None
    products: List[HomepageProductResponse]


class CategoryShowcaseSectionResponse(BaseModel):
    key: str
    title: str
    subtitle: Optional[str] = None
    categories: List[CategoryShowcaseResponse]
