from sqlalchemy import func
from sqlalchemy.orm import Session, joinedload

from app.models.category import Categories
from app.models.homepage_section import HomepageSection
from app.models.product import Product
from app.schemas.homepage_product_schema import (
    CategoryShowcaseFilterSchema,
    CategoryShowcaseResponse,
    CategoryShowcaseSectionResponse,
    FlashSaleFilterSchema,
    FlashSaleSectionResponse,
    HomepageProductResponse,
)


def _get_section(db: Session, section_key: str):
    return (
        db.query(HomepageSection)
        .filter(
            HomepageSection.section_key == section_key,
            HomepageSection.is_active.is_(True),
            HomepageSection.deleted_at.is_(None),
        )
        .first()
    )


def _product_response(product: Product):
    preview = next((image for image in product.images if image.is_preview), None)
    image = preview or (product.images[0] if product.images else None)
    return HomepageProductResponse(
        id=product.id,
        slug=product.slug,
        title=product.title,
        currency=product.currency or "USD",
        price=product.price,
        old_price=product.old_price,
        rating=product.rating,
        sold_count=product.sold_count,
        badge=product.badge,
        image=image.image if image else "/sample-image.png",
    )


def fetch_flash_sale_section(filters: FlashSaleFilterSchema, db: Session):
    section = _get_section(db, "flash_sales")
    if not section:
        return None

    limit = max(1, min(filters.limit, 50))
    products = (
        db.query(Product)
        .options(joinedload(Product.images))
        .filter(Product.is_flash_sale.is_(True), Product.deleted_at.is_(None))
        .order_by(Product.display_order, Product.id)
        .limit(limit)
        .all()
    )
    return FlashSaleSectionResponse(
        key=section.section_key,
        title=section.title,
        subtitle=section.subtitle,
        products=[_product_response(product) for product in products],
    )


def fetch_category_showcase_section(
    filters: CategoryShowcaseFilterSchema,
    db: Session,
):
    section = _get_section(db, "category_showcases")
    if not section:
        return None

    category_limit = max(1, min(filters.limit, 10))
    product_limit = max(1, min(filters.products_per_category, 20))
    categories = (
        db.query(Categories)
        .filter(
            Categories.is_showcase.is_(True),
            Categories.is_active.is_(True),
            Categories.deleted_at.is_(None),
        )
        .order_by(Categories.display_order, Categories.id)
        .limit(category_limit)
        .all()
    )

    showcase_categories = []
    for category in categories:
        products = (
            db.query(Product)
            .options(joinedload(Product.images))
            .filter(Product.category_id == category.id, Product.deleted_at.is_(None))
            .order_by(Product.display_order, Product.id)
            .limit(product_limit)
            .all()
        )
        total_products = (
            db.query(func.count(Product.id))
            .filter(Product.category_id == category.id, Product.deleted_at.is_(None))
            .scalar()
        )
        showcase_categories.append(
            CategoryShowcaseResponse(
                id=category.id,
                slug=category.slug,
                name=category.name,
                tag=category.showcase_tag,
                description=category.showcase_description,
                image=category.showcase_image or category.image or "/sample-image.png",
                button_text=category.showcase_button_text or "Source Now",
                button_url=category.showcase_button_url or f"/products?category={category.slug}",
                total_products=total_products or 0,
                products=[_product_response(product) for product in products],
            )
        )

    return CategoryShowcaseSectionResponse(
        key=section.section_key,
        title=section.title,
        subtitle=section.subtitle,
        categories=showcase_categories,
    )
