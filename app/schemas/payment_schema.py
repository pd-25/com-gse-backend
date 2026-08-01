from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, Field


class CheckoutItemRequest(BaseModel):
    product_id: int = Field(gt=0)
    quantity: int = Field(ge=1, le=100)


class CreatePaymentOrderRequest(BaseModel):
    items: list[CheckoutItemRequest] = Field(min_length=1, max_length=50)


class VerifyPaymentRequest(BaseModel):
    razorpay_order_id: str = Field(min_length=1, max_length=100)
    razorpay_payment_id: str = Field(min_length=1, max_length=100)
    razorpay_signature: str = Field(min_length=1, max_length=200)


class BookingItemResponse(BaseModel):
    product_id: int
    product_title: str
    product_slug: str
    unit_price: Decimal
    quantity: int
    line_total: Decimal


class BookingResponse(BaseModel):
    order_number: str
    status: str
    currency: str
    subtotal: Decimal
    tax: Decimal
    total: Decimal
    razorpay_order_id: str | None
    razorpay_payment_id: str | None
    created_at: datetime
    paid_at: datetime | None
    items: list[BookingItemResponse]


class PaymentOrderResponse(BaseModel):
    key_id: str
    razorpay_order_id: str
    order_number: str
    amount: int
    currency: str
    name: str
    description: str
    customer_name: str
    customer_email: str
    customer_phone: str | None


class PaymentVerificationResponse(BaseModel):
    verified: bool
    booking: BookingResponse
