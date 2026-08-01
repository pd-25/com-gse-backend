from decimal import Decimal
from typing import List, Optional

from pydantic import BaseModel


class CatalogFilterSchema(BaseModel):
    search: Optional[str] = None
    categories: Optional[str] = None
    brands: Optional[str] = None
    min_price: Optional[Decimal] = None
    max_price: Optional[Decimal] = None
    min_rating: Optional[Decimal] = None
    sort: str = "popularity"
    page: int = 1
    per_page: int = 16


class CatalogProductResponse(BaseModel):
    id: int
    slug: str
    title: str
    brand: Optional[str] = None
    currency: str
    price: Decimal
    old_price: Optional[Decimal] = None
    rating: Optional[Decimal] = None
    sold_count: int
    badge: Optional[str] = None
    image: str


class CategoryFacetResponse(BaseModel):
    id: int
    name: str
    slug: str
    count: int


class BrandFacetResponse(BaseModel):
    name: str
    count: int


class RatingFacetResponse(BaseModel):
    value: int
    count: int


class CatalogPageConfigResponse(BaseModel):
    title: str
    subtitle: Optional[str] = None


class CatalogFacetsResponse(BaseModel):
    categories: List[CategoryFacetResponse]
    brands: List[BrandFacetResponse]
    ratings: List[RatingFacetResponse]
    min_price: Decimal
    max_price: Decimal
    page: CatalogPageConfigResponse


class SearchSuggestionFilterSchema(BaseModel):
    q: str = ""
    limit: int = 8


class SearchSuggestionResponse(BaseModel):
    type: str
    label: str
    value: str
    image: Optional[str] = None
