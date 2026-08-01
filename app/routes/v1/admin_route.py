from datetime import UTC, datetime, timedelta
from decimal import Decimal
from uuid import uuid4

import jwt
from fastapi import APIRouter, Depends, File, Form, HTTPException, Query, UploadFile, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from pwdlib import PasswordHash
from sqlalchemy import case, func, or_
from sqlalchemy.orm import Session, joinedload

from app.core.config import settings
from app.database.session import get_db
from app.models.admin import Admin
from app.models.category import Categories
from app.models.footer_setting import FooterLink, FooterSetting
from app.models.hero_banner import HeroBanner
from app.models.homepage_section import HomepageSection
from app.models.order import Order
from app.models.product import Product
from app.models.product_image import ProductImage
from app.models.promotional_card import PromotionalCard
from app.models.user import User
from app.schemas.admin_schema import (
    AdminCreateRequest,
    AdminLoginRequest,
    AdminUpdateRequest,
    CategoryAdminRequest,
    FooterLinkAdminRequest,
    FooterSettingAdminRequest,
    HeroBannerAdminRequest,
    HomepageSectionAdminRequest,
    OrderAdminUpdateRequest,
    ProductAdminRequest,
    PromotionalCardAdminRequest,
    UserAdminUpdateRequest,
)
from app.schemas.response import APIResponse
from app.services.admin_upload_service import upload_admin_image


admin_router = APIRouter()
admin_bearer = HTTPBearer(auto_error=False)
password_hash = PasswordHash.recommended()


def _admin_dict(admin: Admin) -> dict:
    return {
        "id": admin.id,
        "name": admin.name,
        "email": admin.email,
        "is_subadmin": bool(admin.is_subadmin),
        "created_at": admin.created_at,
        "updated_at": admin.updated_at,
    }


def _create_admin_token(admin: Admin) -> str:
    issued_at = datetime.now(UTC)
    return jwt.encode(
        {
            "sub": str(admin.id),
            "email": admin.email,
            "role": "admin",
            "type": "admin_access",
            "iat": issued_at,
            "exp": issued_at + timedelta(hours=8),
            "jti": uuid4().hex,
        },
        settings.SECRET_KEY,
        algorithm=settings.ALGORITHM,
    )


def get_current_admin(
    credentials: HTTPAuthorizationCredentials | None = Depends(admin_bearer),
    db: Session = Depends(get_db),
) -> Admin:
    unauthorized = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Admin authentication required",
        headers={"WWW-Authenticate": "Bearer"},
    )
    if credentials is None or credentials.scheme.lower() != "bearer":
        raise unauthorized
    try:
        payload = jwt.decode(
            credentials.credentials,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM],
        )
        if payload.get("type") != "admin_access" or payload.get("role") != "admin":
            raise unauthorized
        admin_id = int(payload.get("sub", ""))
    except (jwt.InvalidTokenError, TypeError, ValueError):
        raise unauthorized
    admin = db.query(Admin).filter(Admin.id == admin_id, Admin.deleted_at.is_(None)).first()
    if admin is None:
        raise unauthorized
    return admin


def get_current_superadmin(admin: Admin = Depends(get_current_admin)) -> Admin:
    if admin.is_subadmin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Super administrator access required",
        )
    return admin


def _page_meta(total: int, page: int, per_page: int) -> dict:
    return {
        "total": total,
        "page": page,
        "per_page": per_page,
        "total_pages": max(1, (total + per_page - 1) // per_page),
    }


def _search_page(query, page: int, per_page: int):
    total = query.order_by(None).count()
    rows = query.offset((page - 1) * per_page).limit(per_page).all()
    return rows, _page_meta(total, page, per_page)


def _category_dict(category: Categories) -> dict:
    return {
        "id": category.id,
        "name": category.name,
        "slug": category.slug,
        "description": category.description,
        "quality_standards": category.quality_standards,
        "buying_guide": category.buying_guide,
        "image": category.image,
        "thumbnail_image": category.thumbnail_image,
        "showcase_image": category.showcase_image,
        "showcase_tag": category.showcase_tag,
        "showcase_description": category.showcase_description,
        "showcase_button_text": category.showcase_button_text,
        "showcase_button_url": category.showcase_button_url,
        "is_showcase": bool(category.is_showcase),
        "display_order": category.display_order,
        "parent_id": category.parent_id,
        "parent_name": category.parent.name if category.parent else None,
        "is_active": bool(category.is_active),
        "created_at": category.created_at,
        "updated_at": category.updated_at,
    }


def _product_dict(product: Product) -> dict:
    return {
        "id": product.id,
        "slug": product.slug,
        "title": product.title,
        "brand": product.brand,
        "description": product.description,
        "short_desc": product.short_desc,
        "currency": product.currency,
        "price": product.price,
        "old_price": product.old_price,
        "rating": product.rating,
        "sold_count": product.sold_count,
        "badge": product.badge,
        "is_flash_sale": bool(product.is_flash_sale),
        "display_order": product.display_order,
        "price_per_measurement": product.price_per_measurement,
        "min_order": product.min_order,
        "category_id": product.category_id,
        "category_name": product.category.name if product.category else None,
        "subcategory_id": product.subcategory_id,
        "subcategory_name": product.subcategory.name if product.subcategory else None,
        "id_recomended": bool(product.id_recomended),
        "images": [
            {
                "id": image.id,
                "image": image.image,
                "file_type": image.file_type,
                "is_preview": bool(image.is_preview),
            }
            for image in product.images
        ],
        "created_at": product.created_at,
        "updated_at": product.updated_at,
    }


def _hero_dict(banner: HeroBanner) -> dict:
    return {
        "id": banner.id,
        "title": banner.title,
        "subtitle": banner.subtitle,
        "price": banner.price,
        "currency": banner.currency,
        "image": banner.image,
        "button_text": banner.button_text,
        "button_url": banner.button_url,
        "display_order": banner.display_order,
        "is_active": bool(banner.is_active),
        "created_at": banner.created_at,
        "updated_at": banner.updated_at,
    }


def _promotion_dict(card: PromotionalCard) -> dict:
    return {
        "id": card.id,
        "title": card.title,
        "price": card.price,
        "currency": card.currency,
        "image": card.image,
        "button_text": card.button_text,
        "button_url": card.button_url,
        "display_order": card.display_order,
        "is_active": bool(card.is_active),
        "created_at": card.created_at,
        "updated_at": card.updated_at,
    }


def _section_dict(section: HomepageSection) -> dict:
    return {
        "id": section.id,
        "section_key": section.section_key,
        "title": section.title,
        "subtitle": section.subtitle,
        "display_order": section.display_order,
        "is_active": bool(section.is_active),
        "created_at": section.created_at,
        "updated_at": section.updated_at,
    }


def _footer_setting_dict(setting: FooterSetting) -> dict:
    return {column.name: getattr(setting, column.name) for column in setting.__table__.columns}


def _footer_link_dict(link: FooterLink) -> dict:
    return {column.name: getattr(link, column.name) for column in link.__table__.columns}


def _user_dict(user: User) -> dict:
    return {
        "id": user.id,
        "slug": user.slug,
        "first_name": user.first_name,
        "last_name": user.last_name,
        "email": user.email,
        "phone": user.phone,
        "avatar": user.avatar,
        "country": user.country.name if user.country else None,
        "is_active": bool(user.is_active),
        "is_verified": bool(user.is_verified),
        "created_at": user.created_at,
    }


def _order_dict(order: Order) -> dict:
    return {
        "id": order.id,
        "order_number": order.order_number,
        "user_id": order.user_id,
        "customer_name": " ".join(
            filter(None, [order.user.first_name, order.user.last_name])
        ) if order.user else None,
        "customer_email": order.user.email if order.user else None,
        "status": order.status,
        "currency": order.currency,
        "subtotal": order.subtotal,
        "tax": order.tax,
        "total": order.total,
        "razorpay_order_id": order.razorpay_order_id,
        "razorpay_payment_id": order.razorpay_payment_id,
        "created_at": order.created_at,
        "paid_at": order.paid_at,
        "items": [
            {
                "id": item.id,
                "product_id": item.product_id,
                "product_title": item.product_title,
                "quantity": item.quantity,
                "unit_price": item.unit_price,
                "line_total": item.line_total,
            }
            for item in order.items
        ],
    }


@admin_router.post("/auth/login/", response_model=APIResponse[dict])
def admin_login(payload: AdminLoginRequest, db: Session = Depends(get_db)):
    admin = (
        db.query(Admin)
        .filter(Admin.email == payload.email.lower(), Admin.deleted_at.is_(None))
        .first()
    )
    try:
        valid_password = admin is not None and password_hash.verify(payload.password, admin.password)
    except Exception:
        valid_password = False
    if not valid_password or admin is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid admin email or password")
    return APIResponse(
        success=True,
        message="Admin login successful",
        data={"access_token": _create_admin_token(admin), "token_type": "bearer", "admin": _admin_dict(admin)},
    )


@admin_router.get("/auth/me/", response_model=APIResponse[dict])
def admin_me(admin: Admin = Depends(get_current_admin)):
    return APIResponse(success=True, message="Admin profile fetched", data=_admin_dict(admin))


@admin_router.post("/uploads/images/", response_model=APIResponse[dict])
async def upload_image(
    scope: str = Form(default="general"),
    file: UploadFile = File(...),
    _admin: Admin = Depends(get_current_admin),
):
    return APIResponse(
        success=True,
        message="Image uploaded to AWS S3",
        data=await upload_admin_image(file=file, scope=scope),
    )


@admin_router.get("/dashboard/", response_model=APIResponse[dict])
def dashboard(_admin: Admin = Depends(get_current_admin), db: Session = Depends(get_db)):
    paid_total = (
        db.query(func.coalesce(func.sum(Order.total), 0))
        .filter(Order.status.in_(["paid", "processing", "completed"]))
        .scalar()
    )
    recent_orders = (
        db.query(Order)
        .options(joinedload(Order.user), joinedload(Order.items))
        .order_by(Order.created_at.desc())
        .limit(6)
        .all()
    )
    today = datetime.now().date()
    start_date = today - timedelta(days=13)
    paid_statuses = ["paid", "processing", "completed"]
    daily_rows = (
        db.query(
            func.date(Order.created_at).label("day"),
            func.count(Order.id).label("orders"),
            func.coalesce(
                func.sum(case((Order.status.in_(paid_statuses), Order.total), else_=0)),
                0,
            ).label("revenue"),
        )
        .filter(Order.created_at >= datetime.combine(start_date, datetime.min.time()))
        .group_by(func.date(Order.created_at))
        .all()
    )
    daily_lookup = {
        row.day.isoformat() if hasattr(row.day, "isoformat") else str(row.day): row
        for row in daily_rows
    }
    daily_performance = []
    for offset in range(14):
        day = start_date + timedelta(days=offset)
        row = daily_lookup.get(day.isoformat())
        daily_performance.append(
            {
                "date": day.isoformat(),
                "orders": int(row.orders) if row else 0,
                "revenue": row.revenue if row else Decimal("0"),
            }
        )
    status_rows = db.query(Order.status, func.count(Order.id)).group_by(Order.status).all()
    return APIResponse(
        success=True,
        message="Dashboard fetched",
        data={
            "counts": {
                "products": db.query(Product).filter(Product.deleted_at.is_(None)).count(),
                "categories": db.query(Categories).filter(Categories.deleted_at.is_(None)).count(),
                "customers": db.query(User).filter(User.deleted_at.is_(None)).count(),
                "orders": db.query(Order).count(),
                "pending_orders": db.query(Order).filter(Order.status == "pending").count(),
                "active_banners": db.query(HeroBanner).filter(HeroBanner.deleted_at.is_(None), HeroBanner.is_active.is_(True)).count(),
            },
            "paid_revenue": paid_total if isinstance(paid_total, Decimal) else Decimal(str(paid_total)),
            "recent_orders": [_order_dict(order) for order in recent_orders],
            "performance": {
                "daily": daily_performance,
                "statuses": [
                    {"status": row_status, "count": int(count)}
                    for row_status, count in status_rows
                ],
            },
        },
    )


@admin_router.get("/admins/", response_model=APIResponse[list[dict]])
def list_admins(_admin: Admin = Depends(get_current_superadmin), db: Session = Depends(get_db)):
    rows = db.query(Admin).filter(Admin.deleted_at.is_(None)).order_by(Admin.created_at.desc()).all()
    return APIResponse(success=True, message="Administrators fetched", data=[_admin_dict(row) for row in rows])


@admin_router.post("/admins/", response_model=APIResponse[dict], status_code=status.HTTP_201_CREATED)
def create_admin(payload: AdminCreateRequest, _admin: Admin = Depends(get_current_superadmin), db: Session = Depends(get_db)):
    if db.query(Admin.id).filter(Admin.email == payload.email.lower(), Admin.deleted_at.is_(None)).first():
        raise HTTPException(status_code=409, detail="Admin email already exists")
    row = Admin(name=payload.name.strip(), email=payload.email.lower(), password=password_hash.hash(payload.password), is_subadmin=payload.is_subadmin)
    db.add(row)
    db.commit()
    db.refresh(row)
    return APIResponse(success=True, message="Administrator created", data=_admin_dict(row))


@admin_router.patch("/admins/{admin_id}/", response_model=APIResponse[dict])
def update_admin(admin_id: int, payload: AdminUpdateRequest, current: Admin = Depends(get_current_superadmin), db: Session = Depends(get_db)):
    row = db.query(Admin).filter(Admin.id == admin_id, Admin.deleted_at.is_(None)).first()
    if row is None:
        raise HTTPException(status_code=404, detail="Administrator not found")
    values = payload.model_dump(exclude_unset=True)
    if "email" in values:
        email = str(values["email"]).lower()
        if db.query(Admin.id).filter(Admin.email == email, Admin.id != admin_id, Admin.deleted_at.is_(None)).first():
            raise HTTPException(status_code=409, detail="Admin email already exists")
        row.email = email
    if values.get("name") is not None:
        row.name = values["name"].strip()
    if values.get("password") is not None:
        row.password = password_hash.hash(values["password"])
    if "is_subadmin" in values and admin_id != current.id:
        row.is_subadmin = values["is_subadmin"]
    row.updated_at = datetime.now()
    db.commit()
    db.refresh(row)
    return APIResponse(success=True, message="Administrator updated", data=_admin_dict(row))


@admin_router.delete("/admins/{admin_id}/", response_model=APIResponse[None])
def delete_admin(admin_id: int, current: Admin = Depends(get_current_superadmin), db: Session = Depends(get_db)):
    if admin_id == current.id:
        raise HTTPException(status_code=400, detail="You cannot delete your own administrator account")
    row = db.query(Admin).filter(Admin.id == admin_id, Admin.deleted_at.is_(None)).first()
    if row is None:
        raise HTTPException(status_code=404, detail="Administrator not found")
    row.deleted_at = datetime.now()
    db.commit()
    return APIResponse(success=True, message="Administrator deleted", data=None)


@admin_router.get("/categories/", response_model=APIResponse[list[dict]])
def list_categories(search: str = "", page: int = Query(1, ge=1), per_page: int = Query(50, ge=1, le=200), _admin: Admin = Depends(get_current_admin), db: Session = Depends(get_db)):
    query = db.query(Categories).options(joinedload(Categories.parent)).filter(Categories.deleted_at.is_(None))
    if search.strip():
        term = f"%{search.strip()}%"
        query = query.filter(or_(Categories.name.ilike(term), Categories.slug.ilike(term)))
    rows, meta = _search_page(query.order_by(Categories.parent_id, Categories.display_order, Categories.name), page, per_page)
    return APIResponse(success=True, message="Categories fetched", data=[_category_dict(row) for row in rows], meta=meta)


def _validate_category_parent(payload: CategoryAdminRequest, db: Session, category_id: int | None = None):
    if payload.parent_id is None:
        return
    if payload.parent_id == category_id:
        raise HTTPException(status_code=400, detail="A category cannot be its own parent")
    parent = db.query(Categories).filter(Categories.id == payload.parent_id, Categories.deleted_at.is_(None)).first()
    if parent is None or parent.parent_id is not None:
        raise HTTPException(status_code=400, detail="Parent must be an active top-level category")


@admin_router.post("/categories/", response_model=APIResponse[dict], status_code=status.HTTP_201_CREATED)
def create_category(payload: CategoryAdminRequest, _admin: Admin = Depends(get_current_admin), db: Session = Depends(get_db)):
    if db.query(Categories.id).filter(Categories.slug == payload.slug).first():
        raise HTTPException(status_code=409, detail="Category slug already exists")
    _validate_category_parent(payload, db)
    row = Categories(**payload.model_dump())
    db.add(row)
    db.commit()
    db.refresh(row)
    return APIResponse(success=True, message="Category created", data=_category_dict(row))


@admin_router.put("/categories/{category_id}/", response_model=APIResponse[dict])
def update_category(category_id: int, payload: CategoryAdminRequest, _admin: Admin = Depends(get_current_admin), db: Session = Depends(get_db)):
    row = db.query(Categories).filter(Categories.id == category_id, Categories.deleted_at.is_(None)).first()
    if row is None:
        raise HTTPException(status_code=404, detail="Category not found")
    if db.query(Categories.id).filter(Categories.slug == payload.slug, Categories.id != category_id).first():
        raise HTTPException(status_code=409, detail="Category slug already exists")
    _validate_category_parent(payload, db, category_id)
    for key, value in payload.model_dump().items():
        setattr(row, key, value)
    row.updated_at = datetime.now()
    db.commit()
    db.refresh(row)
    return APIResponse(success=True, message="Category updated", data=_category_dict(row))


@admin_router.delete("/categories/{category_id}/", response_model=APIResponse[None])
def delete_category(category_id: int, _admin: Admin = Depends(get_current_admin), db: Session = Depends(get_db)):
    row = db.query(Categories).filter(Categories.id == category_id, Categories.deleted_at.is_(None)).first()
    if row is None:
        raise HTTPException(status_code=404, detail="Category not found")
    if db.query(Categories.id).filter(Categories.parent_id == category_id, Categories.deleted_at.is_(None)).first():
        raise HTTPException(status_code=409, detail="Delete or move subcategories first")
    if db.query(Product.id).filter(or_(Product.category_id == category_id, Product.subcategory_id == category_id), Product.deleted_at.is_(None)).first():
        raise HTTPException(status_code=409, detail="This category is assigned to products")
    row.deleted_at = datetime.now()
    row.is_active = False
    db.commit()
    return APIResponse(success=True, message="Category deleted", data=None)


@admin_router.get("/products/", response_model=APIResponse[list[dict]])
def list_products(search: str = "", page: int = Query(1, ge=1), per_page: int = Query(25, ge=1, le=200), _admin: Admin = Depends(get_current_admin), db: Session = Depends(get_db)):
    query = db.query(Product).options(joinedload(Product.category), joinedload(Product.subcategory), joinedload(Product.images)).filter(Product.deleted_at.is_(None))
    if search.strip():
        term = f"%{search.strip()}%"
        query = query.filter(or_(Product.title.ilike(term), Product.slug.ilike(term), Product.brand.ilike(term)))
    rows, meta = _search_page(query.order_by(Product.display_order, Product.created_at.desc()), page, per_page)
    return APIResponse(success=True, message="Products fetched", data=[_product_dict(row) for row in rows], meta=meta)


def _validate_product_categories(payload: ProductAdminRequest, db: Session):
    if payload.category_id is not None:
        category = db.query(Categories).filter(Categories.id == payload.category_id, Categories.parent_id.is_(None), Categories.deleted_at.is_(None)).first()
        if category is None:
            raise HTTPException(status_code=400, detail="Invalid top-level category")
    if payload.subcategory_id is not None:
        subcategory = db.query(Categories).filter(Categories.id == payload.subcategory_id, Categories.deleted_at.is_(None)).first()
        if subcategory is None or subcategory.parent_id != payload.category_id:
            raise HTTPException(status_code=400, detail="Subcategory must belong to the selected category")


def _replace_product_images(product: Product, payload: ProductAdminRequest):
    product.images.clear()
    for image in payload.images:
        product.images.append(ProductImage(**image.model_dump()))


@admin_router.post("/products/", response_model=APIResponse[dict], status_code=status.HTTP_201_CREATED)
def create_product(payload: ProductAdminRequest, _admin: Admin = Depends(get_current_admin), db: Session = Depends(get_db)):
    if db.query(Product.id).filter(Product.slug == payload.slug).first():
        raise HTTPException(status_code=409, detail="Product slug already exists")
    _validate_product_categories(payload, db)
    values = payload.model_dump(exclude={"images"})
    values["currency"] = payload.currency.upper()
    row = Product(**values)
    _replace_product_images(row, payload)
    db.add(row)
    db.commit()
    db.refresh(row)
    return APIResponse(success=True, message="Product created", data=_product_dict(row))


@admin_router.put("/products/{product_id}/", response_model=APIResponse[dict])
def update_product(product_id: int, payload: ProductAdminRequest, _admin: Admin = Depends(get_current_admin), db: Session = Depends(get_db)):
    row = db.query(Product).options(joinedload(Product.images)).filter(Product.id == product_id, Product.deleted_at.is_(None)).first()
    if row is None:
        raise HTTPException(status_code=404, detail="Product not found")
    if db.query(Product.id).filter(Product.slug == payload.slug, Product.id != product_id).first():
        raise HTTPException(status_code=409, detail="Product slug already exists")
    _validate_product_categories(payload, db)
    for key, value in payload.model_dump(exclude={"images"}).items():
        setattr(row, key, value.upper() if key == "currency" else value)
    _replace_product_images(row, payload)
    row.updated_at = datetime.now()
    db.commit()
    db.refresh(row)
    return APIResponse(success=True, message="Product updated", data=_product_dict(row))


@admin_router.delete("/products/{product_id}/", response_model=APIResponse[None])
def delete_product(product_id: int, _admin: Admin = Depends(get_current_admin), db: Session = Depends(get_db)):
    row = db.query(Product).filter(Product.id == product_id, Product.deleted_at.is_(None)).first()
    if row is None:
        raise HTTPException(status_code=404, detail="Product not found")
    row.deleted_at = datetime.now()
    db.commit()
    return APIResponse(success=True, message="Product deleted", data=None)


@admin_router.get("/hero-banners/", response_model=APIResponse[list[dict]])
def list_hero_banners(_admin: Admin = Depends(get_current_admin), db: Session = Depends(get_db)):
    rows = db.query(HeroBanner).filter(HeroBanner.deleted_at.is_(None)).order_by(HeroBanner.display_order).all()
    return APIResponse(success=True, message="Hero banners fetched", data=[_hero_dict(row) for row in rows])


@admin_router.post("/hero-banners/", response_model=APIResponse[dict], status_code=201)
def create_hero_banner(payload: HeroBannerAdminRequest, _admin: Admin = Depends(get_current_admin), db: Session = Depends(get_db)):
    row = HeroBanner(**payload.model_dump())
    db.add(row); db.commit(); db.refresh(row)
    return APIResponse(success=True, message="Hero banner created", data=_hero_dict(row))


@admin_router.put("/hero-banners/{row_id}/", response_model=APIResponse[dict])
def update_hero_banner(row_id: int, payload: HeroBannerAdminRequest, _admin: Admin = Depends(get_current_admin), db: Session = Depends(get_db)):
    row = db.query(HeroBanner).filter(HeroBanner.id == row_id, HeroBanner.deleted_at.is_(None)).first()
    if row is None: raise HTTPException(status_code=404, detail="Hero banner not found")
    for key, value in payload.model_dump().items(): setattr(row, key, value)
    row.updated_at = datetime.now(); db.commit(); db.refresh(row)
    return APIResponse(success=True, message="Hero banner updated", data=_hero_dict(row))


@admin_router.delete("/hero-banners/{row_id}/", response_model=APIResponse[None])
def delete_hero_banner(row_id: int, _admin: Admin = Depends(get_current_admin), db: Session = Depends(get_db)):
    row = db.query(HeroBanner).filter(HeroBanner.id == row_id, HeroBanner.deleted_at.is_(None)).first()
    if row is None: raise HTTPException(status_code=404, detail="Hero banner not found")
    row.deleted_at = datetime.now(); row.is_active = False; db.commit()
    return APIResponse(success=True, message="Hero banner deleted", data=None)


@admin_router.get("/promotional-cards/", response_model=APIResponse[list[dict]])
def list_promotional_cards(_admin: Admin = Depends(get_current_admin), db: Session = Depends(get_db)):
    rows = db.query(PromotionalCard).filter(PromotionalCard.deleted_at.is_(None)).order_by(PromotionalCard.display_order).all()
    return APIResponse(success=True, message="Promotional cards fetched", data=[_promotion_dict(row) for row in rows])


@admin_router.post("/promotional-cards/", response_model=APIResponse[dict], status_code=201)
def create_promotional_card(payload: PromotionalCardAdminRequest, _admin: Admin = Depends(get_current_admin), db: Session = Depends(get_db)):
    row = PromotionalCard(**payload.model_dump()); db.add(row); db.commit(); db.refresh(row)
    return APIResponse(success=True, message="Promotional card created", data=_promotion_dict(row))


@admin_router.put("/promotional-cards/{row_id}/", response_model=APIResponse[dict])
def update_promotional_card(row_id: int, payload: PromotionalCardAdminRequest, _admin: Admin = Depends(get_current_admin), db: Session = Depends(get_db)):
    row = db.query(PromotionalCard).filter(PromotionalCard.id == row_id, PromotionalCard.deleted_at.is_(None)).first()
    if row is None: raise HTTPException(status_code=404, detail="Promotional card not found")
    for key, value in payload.model_dump().items(): setattr(row, key, value)
    row.updated_at = datetime.now(); db.commit(); db.refresh(row)
    return APIResponse(success=True, message="Promotional card updated", data=_promotion_dict(row))


@admin_router.delete("/promotional-cards/{row_id}/", response_model=APIResponse[None])
def delete_promotional_card(row_id: int, _admin: Admin = Depends(get_current_admin), db: Session = Depends(get_db)):
    row = db.query(PromotionalCard).filter(PromotionalCard.id == row_id, PromotionalCard.deleted_at.is_(None)).first()
    if row is None: raise HTTPException(status_code=404, detail="Promotional card not found")
    row.deleted_at = datetime.now(); row.is_active = False; db.commit()
    return APIResponse(success=True, message="Promotional card deleted", data=None)


@admin_router.get("/homepage-sections/", response_model=APIResponse[list[dict]])
def list_homepage_sections(_admin: Admin = Depends(get_current_admin), db: Session = Depends(get_db)):
    rows = db.query(HomepageSection).filter(HomepageSection.deleted_at.is_(None)).order_by(HomepageSection.display_order).all()
    return APIResponse(success=True, message="Homepage sections fetched", data=[_section_dict(row) for row in rows])


@admin_router.post("/homepage-sections/", response_model=APIResponse[dict], status_code=201)
def create_homepage_section(payload: HomepageSectionAdminRequest, _admin: Admin = Depends(get_current_admin), db: Session = Depends(get_db)):
    if db.query(HomepageSection.id).filter(HomepageSection.section_key == payload.section_key).first(): raise HTTPException(status_code=409, detail="Section key already exists")
    row = HomepageSection(**payload.model_dump()); db.add(row); db.commit(); db.refresh(row)
    return APIResponse(success=True, message="Homepage section created", data=_section_dict(row))


@admin_router.put("/homepage-sections/{row_id}/", response_model=APIResponse[dict])
def update_homepage_section(row_id: int, payload: HomepageSectionAdminRequest, _admin: Admin = Depends(get_current_admin), db: Session = Depends(get_db)):
    row = db.query(HomepageSection).filter(HomepageSection.id == row_id, HomepageSection.deleted_at.is_(None)).first()
    if row is None: raise HTTPException(status_code=404, detail="Homepage section not found")
    if db.query(HomepageSection.id).filter(HomepageSection.section_key == payload.section_key, HomepageSection.id != row_id).first(): raise HTTPException(status_code=409, detail="Section key already exists")
    for key, value in payload.model_dump().items(): setattr(row, key, value)
    row.updated_at = datetime.now(); db.commit(); db.refresh(row)
    return APIResponse(success=True, message="Homepage section updated", data=_section_dict(row))


@admin_router.delete("/homepage-sections/{row_id}/", response_model=APIResponse[None])
def delete_homepage_section(row_id: int, _admin: Admin = Depends(get_current_admin), db: Session = Depends(get_db)):
    row = db.query(HomepageSection).filter(HomepageSection.id == row_id, HomepageSection.deleted_at.is_(None)).first()
    if row is None: raise HTTPException(status_code=404, detail="Homepage section not found")
    row.deleted_at = datetime.now(); row.is_active = False; db.commit()
    return APIResponse(success=True, message="Homepage section deleted", data=None)


@admin_router.get("/footer/settings/", response_model=APIResponse[dict])
def get_footer_settings(_admin: Admin = Depends(get_current_admin), db: Session = Depends(get_db)):
    row = db.query(FooterSetting).order_by(FooterSetting.is_active.desc(), FooterSetting.id).first()
    if row is None: raise HTTPException(status_code=404, detail="Footer settings not found")
    return APIResponse(success=True, message="Footer settings fetched", data=_footer_setting_dict(row))


@admin_router.put("/footer/settings/", response_model=APIResponse[dict])
def update_footer_settings(payload: FooterSettingAdminRequest, _admin: Admin = Depends(get_current_admin), db: Session = Depends(get_db)):
    row = db.query(FooterSetting).order_by(FooterSetting.is_active.desc(), FooterSetting.id).first()
    if row is None:
        row = FooterSetting(**payload.model_dump()); db.add(row)
    else:
        for key, value in payload.model_dump().items(): setattr(row, key, value)
    db.commit(); db.refresh(row)
    return APIResponse(success=True, message="Footer settings updated", data=_footer_setting_dict(row))


@admin_router.get("/footer/links/", response_model=APIResponse[list[dict]])
def list_footer_links(_admin: Admin = Depends(get_current_admin), db: Session = Depends(get_db)):
    rows = db.query(FooterLink).order_by(FooterLink.section, FooterLink.sort_order).all()
    return APIResponse(success=True, message="Footer links fetched", data=[_footer_link_dict(row) for row in rows])


@admin_router.post("/footer/links/", response_model=APIResponse[dict], status_code=201)
def create_footer_link(payload: FooterLinkAdminRequest, _admin: Admin = Depends(get_current_admin), db: Session = Depends(get_db)):
    if payload.slug and db.query(FooterLink.id).filter(FooterLink.slug == payload.slug).first(): raise HTTPException(status_code=409, detail="Footer page slug already exists")
    row = FooterLink(**payload.model_dump()); db.add(row); db.commit(); db.refresh(row)
    return APIResponse(success=True, message="Footer link created", data=_footer_link_dict(row))


@admin_router.put("/footer/links/{row_id}/", response_model=APIResponse[dict])
def update_footer_link(row_id: int, payload: FooterLinkAdminRequest, _admin: Admin = Depends(get_current_admin), db: Session = Depends(get_db)):
    row = db.get(FooterLink, row_id)
    if row is None: raise HTTPException(status_code=404, detail="Footer link not found")
    if payload.slug and db.query(FooterLink.id).filter(FooterLink.slug == payload.slug, FooterLink.id != row_id).first(): raise HTTPException(status_code=409, detail="Footer page slug already exists")
    for key, value in payload.model_dump().items(): setattr(row, key, value)
    db.commit(); db.refresh(row)
    return APIResponse(success=True, message="Footer link updated", data=_footer_link_dict(row))


@admin_router.delete("/footer/links/{row_id}/", response_model=APIResponse[None])
def delete_footer_link(row_id: int, _admin: Admin = Depends(get_current_admin), db: Session = Depends(get_db)):
    row = db.get(FooterLink, row_id)
    if row is None: raise HTTPException(status_code=404, detail="Footer link not found")
    row.is_active = False; db.commit()
    return APIResponse(success=True, message="Footer link deactivated", data=None)


@admin_router.get("/users/", response_model=APIResponse[list[dict]])
def list_users(search: str = "", page: int = Query(1, ge=1), per_page: int = Query(25, ge=1, le=200), _admin: Admin = Depends(get_current_admin), db: Session = Depends(get_db)):
    query = db.query(User).options(joinedload(User.country)).filter(User.deleted_at.is_(None))
    if search.strip():
        term = f"%{search.strip()}%"; query = query.filter(or_(User.first_name.ilike(term), User.last_name.ilike(term), User.email.ilike(term), User.phone.ilike(term)))
    rows, meta = _search_page(query.order_by(User.created_at.desc()), page, per_page)
    return APIResponse(success=True, message="Customers fetched", data=[_user_dict(row) for row in rows], meta=meta)


@admin_router.patch("/users/{user_id}/", response_model=APIResponse[dict])
def update_user(user_id: int, payload: UserAdminUpdateRequest, _admin: Admin = Depends(get_current_admin), db: Session = Depends(get_db)):
    row = db.query(User).filter(User.id == user_id, User.deleted_at.is_(None)).first()
    if row is None: raise HTTPException(status_code=404, detail="Customer not found")
    for key, value in payload.model_dump(exclude_unset=True).items(): setattr(row, key, value)
    row.updated_at = datetime.now(); db.commit(); db.refresh(row)
    return APIResponse(success=True, message="Customer updated", data=_user_dict(row))


@admin_router.get("/orders/", response_model=APIResponse[list[dict]])
def list_orders(search: str = "", order_status: str = "", page: int = Query(1, ge=1), per_page: int = Query(25, ge=1, le=200), _admin: Admin = Depends(get_current_admin), db: Session = Depends(get_db)):
    query = db.query(Order).options(joinedload(Order.user), joinedload(Order.items))
    if search.strip():
        term = f"%{search.strip()}%"; query = query.join(User).filter(or_(Order.order_number.ilike(term), User.email.ilike(term), User.first_name.ilike(term)))
    if order_status.strip(): query = query.filter(Order.status == order_status.strip().lower())
    rows, meta = _search_page(query.order_by(Order.created_at.desc()), page, per_page)
    return APIResponse(success=True, message="Orders fetched", data=[_order_dict(row) for row in rows], meta=meta)


@admin_router.patch("/orders/{order_id}/", response_model=APIResponse[dict])
def update_order(order_id: int, payload: OrderAdminUpdateRequest, _admin: Admin = Depends(get_current_admin), db: Session = Depends(get_db)):
    row = db.query(Order).options(joinedload(Order.user), joinedload(Order.items)).filter(Order.id == order_id).first()
    if row is None: raise HTTPException(status_code=404, detail="Order not found")
    row.status = payload.status
    if payload.status == "paid" and row.paid_at is None: row.paid_at = datetime.now()
    db.commit(); db.refresh(row)
    return APIResponse(success=True, message="Order status updated", data=_order_dict(row))
