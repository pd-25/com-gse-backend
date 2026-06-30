from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models import Categories, Product
from app.schemas.category_schema import CategoryFilterSchema

def fetch_categories(filters: CategoryFilterSchema, db: Session):
    # Subquery to count non-deleted products per category
    product_count = (
        db.query(
            Product.category_id,
            func.count(Product.id).label("total_products")
        )
        .filter(Product.deleted_at == None)
        .group_by(Product.category_id)
        .subquery()
    )

    query = (
        db.query(Categories, func.coalesce(product_count.c.total_products, 0).label("total_products"))
        .outerjoin(product_count, Categories.id == product_count.c.category_id)
        .filter(Categories.deleted_at == None)
    )

    results = query.limit(filters.limit).all()

    # Merge total_products into each category object
    categories = []
    for category, total_products in results:
        category.total_products = total_products
        categories.append(category)

    return categories