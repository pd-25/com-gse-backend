from fastapi import APIRouter, Depends, Request, status
from fastapi.responses import HTMLResponse, RedirectResponse
from urllib.parse import urlencode
from sqlalchemy.orm import Session

from app.core.config import settings
from app.database.session import get_db
from app.models.user import User
from app.schemas.payment_schema import (
    BookingResponse,
    CreatePaymentOrderRequest,
    CreateSSLCommerzOrderRequest,
    PaymentOrderResponse,
    PaymentVerificationResponse,
    SSLCommerzNotificationResponse,
    SSLCommerzOrderResponse,
    VerifyPaymentRequest,
)
from app.schemas.response import APIResponse
from app.services.auth_service import get_current_user
from app.services.payment_service import (
    create_payment_order,
    create_sslcommerz_order,
    fetch_bookings,
    generate_invoice_html,
    process_sslcommerz_notification,
    verify_payment,
)


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


@payment_router.post(
    "/sslcommerz/orders/",
    response_model=APIResponse[SSLCommerzOrderResponse],
    status_code=status.HTTP_201_CREATED,
)
def create_sslcommerz_payment_order(
    payload: CreateSSLCommerzOrderRequest,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return APIResponse(
        success=True,
        message="SSLCommerz payment session created successfully",
        data=create_sslcommerz_order(payload=payload, user=user, db=db),
    )


async def _handle_sslcommerz_notification(request: Request, db: Session):
    form = {key: str(value) for key, value in (await request.form()).items()}
    order = process_sslcommerz_notification(form=form, db=db)
    if settings.SSLCOMMERZ_FRONTEND_RETURN_URL and request.url.path.rstrip("/").endswith(("success", "fail", "cancel")):
        query = urlencode({"provider": "sslcommerz", "order_number": order.order_number, "status": order.status})
        separator = "&" if "?" in settings.SSLCOMMERZ_FRONTEND_RETURN_URL else "?"
        return RedirectResponse(f"{settings.SSLCOMMERZ_FRONTEND_RETURN_URL}{separator}{query}", status_code=303)
    return APIResponse(
        success=order.status == "paid",
        message=f"SSLCommerz payment status: {order.status}",
        data=SSLCommerzNotificationResponse(
            transaction_id=order.sslcommerz_transaction_id,
            order_number=order.order_number,
            status=order.status,
        ),
    )


@payment_router.post("/sslcommerz/success/", response_model=None)
async def sslcommerz_success(request: Request, db: Session = Depends(get_db)):
    return await _handle_sslcommerz_notification(request, db)


@payment_router.post("/sslcommerz/fail/", response_model=None)
async def sslcommerz_fail(request: Request, db: Session = Depends(get_db)):
    return await _handle_sslcommerz_notification(request, db)


@payment_router.post("/sslcommerz/cancel/", response_model=None)
async def sslcommerz_cancel(request: Request, db: Session = Depends(get_db)):
    return await _handle_sslcommerz_notification(request, db)


@payment_router.post("/sslcommerz/ipn/", response_model=APIResponse[SSLCommerzNotificationResponse])
async def sslcommerz_ipn(request: Request, db: Session = Depends(get_db)):
    return await _handle_sslcommerz_notification(request, db)


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


@payment_router.get(
    "/bookings/{order_number}/invoice/",
    response_class=HTMLResponse,
)
def get_booking_invoice(
    order_number: str,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return HTMLResponse(
        content=generate_invoice_html(order_number=order_number, user=user, db=db),
        headers={"Content-Disposition": f'inline; filename="{order_number}-invoice.html"'},
    )
