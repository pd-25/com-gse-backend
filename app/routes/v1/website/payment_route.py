from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.models.user import User
from app.schemas.payment_schema import (
    BookingResponse,
    CreatePaymentOrderRequest,
    PaymentOrderResponse,
    PaymentVerificationResponse,
    VerifyPaymentRequest,
)
from app.schemas.response import APIResponse
from app.services.auth_service import get_current_user
from app.services.payment_service import create_payment_order, fetch_bookings, verify_payment


payment_router = APIRouter()


@payment_router.post(
    "/orders/",
    response_model=APIResponse[PaymentOrderResponse],
    status_code=status.HTTP_201_CREATED,
)
def create_order(
    payload: CreatePaymentOrderRequest,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return APIResponse(
        success=True,
        message="Razorpay order created successfully",
        data=create_payment_order(payload=payload, user=user, db=db),
    )


@payment_router.post("/verify/", response_model=APIResponse[PaymentVerificationResponse])
def verify_order_payment(
    payload: VerifyPaymentRequest,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return APIResponse(
        success=True,
        message="Payment verified and product booking confirmed",
        data=verify_payment(payload=payload, user=user, db=db),
    )


@payment_router.get("/bookings/", response_model=APIResponse[list[BookingResponse]])
def get_bookings(
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return APIResponse(
        success=True,
        message="Bookings fetched successfully",
        data=fetch_bookings(user=user, db=db),
    )
