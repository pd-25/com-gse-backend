import base64
import hashlib
import hmac
import json
from html import escape
from datetime import datetime
from decimal import Decimal, ROUND_HALF_UP
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen
from uuid import uuid4

from fastapi import HTTPException, status
from sqlalchemy.orm import Session, joinedload

from app.core.config import settings
from app.models.order import Order, OrderItem
from app.models.product import Product
from app.models.user import User
from app.schemas.payment_schema import (
    BookingItemResponse,
    BookingResponse,
    CreatePaymentOrderRequest,
    PaymentOrderResponse,
    PaymentVerificationResponse,
    VerifyPaymentRequest,
)


BRAND_NAME = "Global Source Expo Ltd"


def _require_razorpay_config() -> tuple[str, str]:
    if not settings.RAZORPAY_KEY_ID or not settings.RAZORPAY_KEY_SECRET:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Razorpay test credentials are not configured",
        )
    return settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET


def _payment_price(price: Decimal, source_currency: str | None) -> Decimal:
    target = settings.RAZORPAY_PAYMENT_CURRENCY
    source = (source_currency or "USD").upper()
    if source == target:
        converted = price
    elif source == "USD" and target == "INR":
        converted = price * Decimal(settings.USD_TO_INR_RATE)
    else:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Payment conversion from {source} to {target} is not configured",
        )
    return converted.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)


def _amount_subunits(amount: Decimal) -> int:
    return int((amount * 100).quantize(Decimal("1"), rounding=ROUND_HALF_UP))


def _razorpay_create_order(amount: int, currency: str, receipt: str, notes: dict) -> dict:
    key_id, key_secret = _require_razorpay_config()
    credentials = base64.b64encode(f"{key_id}:{key_secret}".encode()).decode()
    request = Request(
        "https://api.razorpay.com/v1/orders",
        data=json.dumps(
            {
                "amount": amount,
                "currency": currency,
                "receipt": receipt,
                "notes": notes,
            }
        ).encode(),
        headers={
            "Authorization": f"Basic {credentials}",
            "Content-Type": "application/json",
        },
        method="POST",
    )
    try:
        with urlopen(request, timeout=15) as response:
            return json.load(response)
    except HTTPError as error:
        try:
            provider_error = json.load(error)
            message = provider_error.get("error", {}).get("description")
        except (json.JSONDecodeError, AttributeError):
            message = None
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=message or "Razorpay rejected the order request",
        )
    except URLError:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Unable to connect to Razorpay",
        )


def _booking_response(order: Order) -> BookingResponse:
    return BookingResponse(
        order_number=order.order_number,
        status=order.status,
        currency=order.currency,
        subtotal=order.subtotal,
        tax=order.tax,
        total=order.total,
        razorpay_order_id=order.razorpay_order_id,
        razorpay_payment_id=order.razorpay_payment_id,
        created_at=order.created_at,
        paid_at=order.paid_at,
        items=[
            BookingItemResponse(
                product_id=item.product_id,
                product_title=item.product_title,
                product_slug=item.product_slug,
                unit_price=item.unit_price,
                quantity=item.quantity,
                line_total=item.line_total,
            )
            for item in order.items
        ],
    )


def create_payment_order(
    payload: CreatePaymentOrderRequest,
    user: User,
    db: Session,
) -> PaymentOrderResponse:
    key_id, _key_secret = _require_razorpay_config()
    quantities: dict[int, int] = {}
    for item in payload.items:
        quantities[item.product_id] = quantities.get(item.product_id, 0) + item.quantity
        if quantities[item.product_id] > 100:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="A product quantity cannot exceed 100",
            )

    products = (
        db.query(Product)
        .filter(Product.id.in_(quantities), Product.deleted_at.is_(None))
        .all()
    )
    product_by_id = {product.id: product for product in products}
    missing = sorted(set(quantities) - set(product_by_id))
    if missing:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Products not found: {', '.join(map(str, missing))}",
        )

    currency = settings.RAZORPAY_PAYMENT_CURRENCY
    order_number = f"GSE-{datetime.now():%Y%m%d}-{uuid4().hex[:8].upper()}"
    receipt = f"gse_{uuid4().hex[:20]}"
    order = Order(
        order_number=order_number,
        user_id=user.id,
        status="pending",
        currency=currency,
        subtotal=Decimal("0"),
        tax=Decimal("0"),
        total=Decimal("0"),
        receipt=receipt,
    )
    for product_id, quantity in quantities.items():
        product = product_by_id[product_id]
        if product.price is None or product.price <= 0:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=f"Product {product_id} is not available for payment",
            )
        unit_price = _payment_price(product.price, product.currency)
        line_total = unit_price * quantity
        order.items.append(
            OrderItem(
                product_id=product.id,
                product_title=product.title,
                product_slug=product.slug,
                unit_price=unit_price,
                quantity=quantity,
                line_total=line_total,
            )
        )
        order.subtotal += line_total
    order.total = order.subtotal + order.tax

    razorpay_order = _razorpay_create_order(
        amount=_amount_subunits(order.total),
        currency=order.currency,
        receipt=order.receipt,
        notes={"local_order_number": order.order_number, "customer_email": user.email},
    )
    order.razorpay_order_id = razorpay_order["id"]
    db.add(order)
    db.commit()
    db.refresh(order)

    return PaymentOrderResponse(
        key_id=key_id,
        razorpay_order_id=order.razorpay_order_id,
        order_number=order.order_number,
        amount=_amount_subunits(order.total),
        currency=order.currency,
        name=BRAND_NAME,
        description=f"Payment for booking {order.order_number}",
        customer_name=" ".join(filter(None, [user.first_name, user.last_name])),
        customer_email=user.email,
        customer_phone=user.phone,
    )


def verify_payment(
    payload: VerifyPaymentRequest,
    user: User,
    db: Session,
) -> PaymentVerificationResponse:
    _key_id, key_secret = _require_razorpay_config()
    order = (
        db.query(Order)
        .options(joinedload(Order.items))
        .filter(
            Order.razorpay_order_id == payload.razorpay_order_id,
            Order.user_id == user.id,
        )
        .first()
    )
    if order is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Payment order not found")
    if order.status == "paid":
        if order.razorpay_payment_id != payload.razorpay_payment_id:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Order is already paid")
        return PaymentVerificationResponse(verified=True, booking=_booking_response(order))

    message = f"{order.razorpay_order_id}|{payload.razorpay_payment_id}".encode()
    expected = hmac.new(key_secret.encode(), message, hashlib.sha256).hexdigest()
    if not hmac.compare_digest(expected, payload.razorpay_signature):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Payment signature verification failed",
        )

    order.status = "paid"
    order.razorpay_payment_id = payload.razorpay_payment_id
    order.paid_at = datetime.now()
    db.commit()
    db.refresh(order)
    return PaymentVerificationResponse(verified=True, booking=_booking_response(order))


def fetch_bookings(user: User, db: Session) -> list[BookingResponse]:
    orders = (
        db.query(Order)
        .options(joinedload(Order.items))
        .filter(Order.user_id == user.id)
        .order_by(Order.created_at.desc(), Order.id.desc())
        .all()
    )
    return [_booking_response(order) for order in orders]


def generate_invoice_html(order_number: str, user: User, db: Session) -> str:
    order = (
        db.query(Order)
        .options(joinedload(Order.items))
        .filter(Order.order_number == order_number, Order.user_id == user.id)
        .first()
    )
    if order is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Booking not found")

    def money(value: Decimal) -> str:
        return f"{order.currency} {value:,.2f}"

    item_rows = "".join(
        f"""
        <tr>
          <td>{escape(item.product_title)}</td>
          <td class="number">{item.quantity}</td>
          <td class="number">{money(item.unit_price)}</td>
          <td class="number">{money(item.line_total)}</td>
        </tr>
        """
        for item in order.items
    )
    payment_reference = escape(order.razorpay_payment_id or "Awaiting payment")
    paid_label = order.paid_at.strftime("%d %b %Y, %I:%M %p") if order.paid_at else "Not paid"
    customer_name = escape(" ".join(filter(None, [user.first_name, user.last_name])))
    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Invoice {escape(order.order_number)} | {BRAND_NAME}</title>
  <style>
    * {{ box-sizing: border-box; }}
    body {{ margin: 0; padding: 32px; color: #17211d; font: 14px/1.5 Arial, sans-serif; background: #f5f7f6; }}
    .invoice {{ max-width: 900px; margin: auto; padding: 44px; background: #fff; border-top: 6px solid #75b900; box-shadow: 0 8px 28px #0001; }}
    header {{ display: flex; justify-content: space-between; gap: 24px; padding-bottom: 28px; border-bottom: 1px solid #dfe5e2; }}
    h1 {{ margin: 0; color: #054934; font-size: 28px; }}
    .brand {{ color: #054934; font-size: 22px; font-weight: 800; }}
    .muted {{ color: #68736e; }}
    .status {{ display: inline-block; margin-top: 8px; padding: 5px 12px; border-radius: 99px; background: #e8f4cf; color: #426600; font-weight: 700; text-transform: uppercase; }}
    .details {{ display: grid; grid-template-columns: 1fr 1fr; gap: 24px; margin: 28px 0; }}
    table {{ width: 100%; border-collapse: collapse; }}
    th, td {{ padding: 12px 10px; border-bottom: 1px solid #e6ebe8; text-align: left; }}
    th {{ background: #f2f7e9; color: #054934; }}
    .number {{ text-align: right; white-space: nowrap; }}
    .totals {{ width: min(360px, 100%); margin: 24px 0 0 auto; }}
    .totals div {{ display: flex; justify-content: space-between; padding: 6px 0; }}
    .grand {{ margin-top: 8px; padding-top: 12px !important; border-top: 2px solid #054934; color: #054934; font-size: 18px; font-weight: 800; }}
    .actions {{ max-width: 900px; margin: 16px auto; text-align: right; }}
    button {{ border: 0; border-radius: 8px; padding: 10px 18px; color: #fff; background: #054934; cursor: pointer; }}
    footer {{ margin-top: 40px; padding-top: 18px; border-top: 1px solid #dfe5e2; color: #68736e; text-align: center; }}
    @media print {{ body {{ padding: 0; background: #fff; }} .invoice {{ box-shadow: none; }} .actions {{ display: none; }} }}
    @media (max-width: 600px) {{ body {{ padding: 12px; }} .invoice {{ padding: 24px; }} header, .details {{ display: block; }} header > div + div, .details > div + div {{ margin-top: 18px; }} }}
  </style>
</head>
<body>
  <div class="actions"><button type="button" onclick="window.print()">Print / Save as PDF</button></div>
  <main class="invoice">
    <header>
      <div><div class="brand">{BRAND_NAME}</div><div class="muted">Product Booking Invoice</div></div>
      <div><h1>INVOICE</h1><div><strong>{escape(order.order_number)}</strong></div><span class="status">{escape(order.status)}</span></div>
    </header>
    <section class="details">
      <div><strong>Bill To</strong><br>{customer_name}<br>{escape(user.email)}<br>{escape(user.phone or "")}</div>
      <div><strong>Booking Date</strong><br>{order.created_at:%d %b %Y, %I:%M %p}<br><br><strong>Payment Date</strong><br>{paid_label}</div>
    </section>
    <table>
      <thead><tr><th>Product</th><th class="number">Quantity</th><th class="number">Unit Price</th><th class="number">Amount</th></tr></thead>
      <tbody>{item_rows}</tbody>
    </table>
    <section class="totals">
      <div><span>Subtotal</span><strong>{money(order.subtotal)}</strong></div>
      <div><span>Tax</span><strong>{money(order.tax)}</strong></div>
      <div class="grand"><span>Total</span><span>{money(order.total)}</span></div>
    </section>
    <section class="details">
      <div><strong>Razorpay Order</strong><br>{escape(order.razorpay_order_id or "Not created")}</div>
      <div><strong>Payment Reference</strong><br>{payment_reference}</div>
    </section>
    <footer>Thank you for booking with {BRAND_NAME}.</footer>
  </main>
</body>
</html>"""
