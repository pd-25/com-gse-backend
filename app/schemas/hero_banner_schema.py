from decimal import Decimal
from typing import Optional

from pydantic import BaseModel


class HeroBannerFilterSchema(BaseModel):
    limit: int = 10


class HeroBannerListResponse(BaseModel):
    id: int
    title: str
    subtitle: Optional[str] = None
    price: Optional[Decimal] = None
    currency: str
    image: str
    button_text: str
    button_url: str
    display_order: int
