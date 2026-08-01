import math

from sqlalchemy import and_, func, or_
from sqlalchemy.orm import Session, joinedload

from app.core.rich_text import sanitize_rich_text
from app.models.category import Categories
from app.models.homepage_section import HomepageSection
from app.models.product import Product
from app.schemas.catalog_schema import (
    BrandFacetResponse,
    CatalogFacetsResponse,
    CatalogFilterSchema,
    CatalogPageConfigResponse,
    CatalogProductResponse,
    CategoryFacetResponse,
    RatingFacetResponse,
    SearchSuggestionFilterSchema,
    SearchSuggestionResponse,
)


def _csv_values(value: str | None):
    return [item.strip() for item in (value or "").split(",") if item.strip()]


def _product_image(product: Product):
    preview = next((image for image in product.images if image.is_preview), None)
    image = preview or (product.images[0] if product.images else None)
    return image.image if image else "/sample-image.png"


def _product_response(product: Product):
    return CatalogProductResponse(
        id=product.id,
        slug=product.slug,
        title=product.title,
        brand=product.brand,
        description=sanitize_rich_text(product.description),
        short_desc=product.short_desc,
        currency=product.currency or "USD",
        price=product.price,
        old_price=product.old_price,
        rating=product.rating,
        sold_count=product.sold_count,
        badge=product.badge,
        image=_product_image(product),
    )


def fetch_catalog_facets(db: Session):
    category_rows = (
        db.query(
            Categories.id,
            Categories.name,
            Categories.slug,
            func.count(Product.id).label("count"),
        )
        .outerjoin(
            Product,
            and_(Product.category_id == Categories.id, Product.deleted_at.is_(None)),
        )
        .filter(
            Categories.parent_id.is_(None),
            Categories.is_active.is_(True),
            Categories.deleted_at.is_(None),
        )
        .group_by(Categories.id, Categories.name, Categories.slug)
        .order_by(Categories.display_order, Categories.id)
        .all()
    )
    categories = [
        CategoryFacetResponse(id=row.id, name=row.name, slug=row.slug, count=row.count)
        for row in category_rows
    ]

    brand_rows = (
        db.query(Product.brand, func.count(Product.id).label("count"))
        .filter(Product.brand.is_not(None), Product.deleted_at.is_(None))
        .group_by(Product.brand)
        .order_by(func.count(Product.id).desc(), Product.brand)
        .all()
    )
    brands = [BrandFacetResponse(name=row.brand, count=row.count) for row in brand_rows]

    ratings = []
    for value in (4, 3, 2, 1):
        count = (
            db.query(func.count(Product.id))
            .filter(Product.rating >= value, Product.deleted_at.is_(None))
            .scalar()
        )
        ratings.append(RatingFacetResponse(value=value, count=count or 0))

    min_price, max_price = (
        db.query(func.min(Product.price), func.max(Product.price))
        .filter(Product.deleted_at.is_(None))
        .one()
    )
    page_section = (
        db.query(HomepageSection)
        .filter(
            HomepageSection.section_key == "product_catalog",
            HomepageSection.is_active.is_(True),
            HomepageSection.deleted_at.is_(None),
        )
        .first()
    )
    page = CatalogPageConfigResponse(
        title=page_section.title if page_section else "Shop All Products",
        subtitle=page_section.subtitle if page_section else None,
    )
    return CatalogFacetsResponse(
        categories=categories,
        brands=brands,
        ratings=ratings,
        min_price=min_price or 0,
        max_price=max_price or 0,
        page=page,
    )


def fetch_catalog_products(filters: CatalogFilterSchema, db: Session):
    page = max(1, filters.page)
    per_page = max(1, min(filters.per_page, 48))
    query = db.query(Product).options(joinedload(Product.images)).filter(Product.deleted_at.is_(None))

    if filters.search and filters.search.strip():
        term = f"%{filters.search.strip()}%"
        query = query.filter(
            or_(
                Product.title.ilike(term),
                Product.brand.ilike(term),
                Product.slug.ilike(term),
            )
        )

    category_slugs = _csv_values(filters.categories)
    if category_slugs:
        query = query.join(
            Categories,
            Product.category_id == Categories.id,
        ).filter(Categories.slug.in_(category_slugs))

    brands = _csv_values(filters.brands)
    if brands:
        query = query.filter(Product.brand.in_(brands))

    if filters.min_price is not None:
        query = query.filter(Product.price >= filters.min_price)
    if filters.max_price is not None:
        query = query.filter(Product.price <= filters.max_price)
    if filters.min_rating is not None:
        query = query.filter(Product.rating >= filters.min_rating)

    total = query.count()
    sort_map = {
        "popularity": (Product.sold_count.desc(), Product.id.desc()),
        "price_asc": (Product.price.asc(), Product.id.asc()),
        "price_desc": (Product.price.desc(), Product.id.asc()),
        "rating": (Product.rating.desc(), Product.sold_count.desc()),
        "newest": (Product.id.desc(),),
    }
    order_by = sort_map.get(filters.sort, sort_map["popularity"])
    products = query.order_by(*order_by).offset((page - 1) * per_page).limit(per_page).all()
    total_pages = max(1, math.ceil(total / per_page)) if total else 0
    first = ((page - 1) * per_page) + 1 if total else 0
    last = min(page * per_page, total)

    return (
        [_product_response(product) for product in products],
        {
            "page": page,
            "per_page": per_page,
            "total": total,
            "total_pages": total_pages,
            "from": first,
            "to": last,
            "facets": fetch_catalog_facets(db).model_dump(mode="json"),
        },
    )


def fetch_search_suggestions(filters: SearchSuggestionFilterSchema, db: Session):
    query_text = filters.q.strip()
    if len(query_text) < 2:
        return []

    limit = max(1, min(filters.limit, 12))
    term = f"%{query_text}%"
    products = (
        db.query(Product)
        .options(joinedload(Product.images))
        .filter(
            Product.deleted_at.is_(None),
            or_(Product.title.ilike(term), Product.brand.ilike(term)),
        )
        .order_by(Product.sold_count.desc())
        .limit(limit)
        .all()
    )
    suggestions = [
        SearchSuggestionResponse(
            type="product",
            label=product.title,
            value=product.title,
            image=_product_image(product),
        )
        for product in products
    ]

    remaining = limit - len(suggestions)
    if remaining > 0:
        categories = (
            db.query(Categories)
            .filter(
                Categories.deleted_at.is_(None),
                Categories.is_active.is_(True),
                Categories.name.ilike(term),
            )
            .limit(remaining)
            .all()
        )
        suggestions.extend(
            SearchSuggestionResponse(
                type="category",
                label=category.name,
                value=category.slug,
                image=category.thumbnail_image or category.image,
            )
            for category in categories
        )
    return suggestions
