from fastapi import HTTPException, status
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.core.rich_text import sanitize_rich_text
from app.models import Categories, Product
from app.models.product_image import ProductImage
from app.schemas.category_schema import (
    CategoryDetailInfo,
    CategoryDetailResponse,
    CategoryFilterSchema,
    CategoryListResponse,
    CategoryPriceSummary,
    CategoryProductResponse,
    SubcategoryResponse,
)


def _category_detail_info(category: Categories) -> CategoryDetailInfo:
    return CategoryDetailInfo(
        id=category.id,
        slug=category.slug,
        name=category.name,
        description=sanitize_rich_text(category.description),
        quality_standards=sanitize_rich_text(category.quality_standards),
        buying_guide=sanitize_rich_text(category.buying_guide),
        image=category.image,
        thumbnail_image=category.thumbnail_image,
    )


def fetch_categories(filters: CategoryFilterSchema, db: Session):
    # Subquery to count non-deleted products per category
    product_count = (
        db.query(Product.category_id, func.count(Product.id).label("total_products"))
        .filter(Product.deleted_at == None)
        .group_by(Product.category_id)
        .subquery()
    )

    query = (
        db.query(
            Categories.id,
            Categories.slug,
            Categories.name,
            Categories.image,
            Categories.thumbnail_image,
            func.coalesce(product_count.c.total_products, 0).label("total_products"),
        )
        .outerjoin(product_count, Categories.id == product_count.c.category_id)
        .filter(
            Categories.deleted_at.is_(None),
            Categories.parent_id.is_(None),
            Categories.is_active.is_(True),
        )
        .order_by(Categories.display_order, Categories.id)
    )

    results = query.limit(filters.limit).all()
    # 1st return
    # return results

    # 2nd return
    # # Merge total_products into each category object
    # categories = []
    # for category, total_products in results:
    #     category.total_products = total_products
    #     categories.append(category)
    # return categories
    # 3rd return
    return [CategoryListResponse.model_validate(row._mapping) for row in results]


def fetch_category_detail(slug: str, db: Session) -> CategoryDetailResponse:
    category = (
        db.query(Categories)
        .filter(
            Categories.slug == slug,
            Categories.parent_id.is_(None),
            Categories.deleted_at.is_(None),
            Categories.is_active.is_(True),
        )
        .first()
    )
    if category is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Category not found")

    subcategory_rows = (
        db.query(
            Categories,
            func.count(Product.id).label("total_products"),
            func.min(Product.price).label("min_price"),
            func.max(Product.price).label("max_price"),
        )
        .outerjoin(Product, Product.subcategory_id == Categories.id)
        .filter(
            Categories.parent_id == category.id,
            Categories.deleted_at.is_(None),
            Categories.is_active.is_(True),
        )
        .group_by(Categories.id)
        .order_by(Categories.display_order, Categories.id)
        .all()
    )

    product_rows = (
        db.query(Product, ProductImage.image, Categories.slug, Categories.name)
        .outerjoin(ProductImage, ProductImage.id == (
            db.query(func.min(ProductImage.id))
            .filter(ProductImage.product_id == Product.id)
            .correlate(Product)
            .scalar_subquery()
        ))
        .outerjoin(Categories, Categories.id == Product.subcategory_id)
        .filter(Product.category_id == category.id, Product.deleted_at.is_(None))
        .order_by(Product.display_order, Product.id)
        .all()
    )

    products = [
        CategoryProductResponse(
            id=product.id,
            slug=product.slug,
            title=product.title,
            brand=product.brand,
            description=sanitize_rich_text(product.description),
            short_desc=product.short_desc,
            currency=product.currency or "USD",
            price=float(product.price),
            old_price=float(product.old_price) if product.old_price is not None else None,
            rating=float(product.rating) if product.rating is not None else None,
            sold_count=product.sold_count,
            badge=product.badge,
            image=image or "/sample-image.png",
            subcategory_id=product.subcategory_id,
            subcategory_slug=subcategory_slug,
            subcategory_name=subcategory_name,
        )
        for product, image, subcategory_slug, subcategory_name in product_rows
    ]
    prices = [product.price for product in products]
    ratings = [product.rating for product in products if product.rating is not None]

    return CategoryDetailResponse(
        category=_category_detail_info(category),
        subcategories=[
            SubcategoryResponse(
                **_category_detail_info(child).model_dump(),
                total_products=total_products,
                min_price=float(min_price) if min_price is not None else None,
                max_price=float(max_price) if max_price is not None else None,
            )
            for child, total_products, min_price, max_price in subcategory_rows
        ],
        products=products,
        summary=CategoryPriceSummary(
            currency=products[0].currency if products else "USD",
            min_price=min(prices) if prices else None,
            max_price=max(prices) if prices else None,
            average_rating=round(sum(ratings) / len(ratings), 1) if ratings else None,
            total_products=len(products),
        ),
    )
