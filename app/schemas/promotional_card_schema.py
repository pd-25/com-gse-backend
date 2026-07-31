from decimal import Decimal

from pydantic import BaseModel


class PromotionalCardFilterSchema(BaseModel):
    limit: int = 10


class PromotionalCardListResponse(BaseModel):
    id: int
    title: str
    price: Decimal
    currency: str
    image: str
    button_text: str
    button_url: str
    display_order: int
