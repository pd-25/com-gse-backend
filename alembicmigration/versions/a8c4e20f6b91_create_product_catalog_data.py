"""create product catalog data

Revision ID: a8c4e20f6b91
Revises: f3a9b62d8e10
Create Date: 2026-08-01 14:00:00.000000

"""
import re
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op


revision: str = "a8c4e20f6b91"
down_revision: Union[str, Sequence[str], None] = "f3a9b62d8e10"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def _slugify(value: str):
    return re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")


def _catalog_products():
    category_products = {
        1: [
            ("Premium Cavendish Bananas Box", "Fresh Fields", 18.99, 4.7, 742),
            ("Sweet Valencia Oranges Carton", "Sun Valley", 24.50, 4.2, 518),
            ("Seedless Green Grapes Pack", "Orchard Select", 12.75, 3.8, 326),
            ("Fresh Strawberry Punnet", "Berry Best", 9.99, 4.9, 1104),
        ],
        2: [
            ("Organic Baby Carrots", "Organic Valley", 6.49, 4.5, 688),
            ("Vine Ripened Tomatoes", "Green Harvest", 8.25, 3.6, 459),
            ("Mixed Bell Peppers", "Fresh Fields", 10.99, 4.1, 577),
            ("Organic English Cucumbers", "Green Harvest", 7.49, 4.8, 832),
        ],
        3: [
            ("Farm Fresh Whole Milk", "Dairy Pure", 5.99, 4.6, 1387),
            ("Mature Cheddar Cheese Block", "Organic Valley", 11.50, 4.4, 926),
            ("Natural Greek Yogurt Pack", "Dairy Pure", 8.99, 3.9, 614),
            ("Salted Creamery Butter", "Meadow Gold", 7.25, 4.7, 1008),
        ],
        4: [
            ("French Butter Croissants", "Daily Bake", 13.99, 4.3, 751),
            ("New York Style Bagels", "Daily Bake", 9.50, 3.4, 483),
            ("Artisan Brioche Loaf", "Golden Grain", 8.75, 4.8, 695),
            ("Blueberry Breakfast Muffins", "Golden Grain", 12.25, 4.1, 544),
        ],
        5: [
            ("Premium Chicken Breast Fillets", "Prime Cuts", 34.99, 4.8, 821),
            ("Grass Fed Beef Sirloin", "Prime Cuts", 64.50, 4.6, 418),
            ("Atlantic Salmon Portions", "Ocean Catch", 42.99, 4.9, 603),
            ("Raw King Prawns Pack", "Ocean Catch", 38.75, 3.7, 294),
        ],
        6: [
            ("Sea Salt Potato Chips", "Kettle Brand", 4.99, 4.2, 1682),
            ("Roasted Almond Snack Packs", "Blue Diamond", 14.50, 4.7, 934),
            ("Dark Chocolate Sharing Bar", "Cocoa House", 6.75, 3.3, 721),
            ("Honey Oat Granola Bars", "Nature's Path", 8.99, 4.5, 1156),
        ],
    }
    rows = []
    product_id = 21
    for category_id, products in category_products.items():
        for position, (title, brand, price, rating, sold_count) in enumerate(products, start=1):
            rows.append(
                {
                    "id": product_id,
                    "slug": _slugify(title),
                    "title": title,
                    "brand": brand,
                    "short_desc": "Quality wholesale product from a verified supplier.",
                    "currency": "USD",
                    "price": price,
                    "old_price": round(price * 1.25, 2),
                    "rating": rating,
                    "sold_count": sold_count,
                    "badge": "Best Sale" if position == 1 else ("New" if position == 4 else None),
                    "is_flash_sale": False,
                    "display_order": position,
                    "product_type_id": 1,
                    "category_id": category_id,
                    "id_recomended": position <= 2,
                }
            )
            product_id += 1
    return rows


def upgrade() -> None:
    op.add_column("products", sa.Column("brand", sa.String(length=150), nullable=True))

    brand_updates = {
        "Fresh Market": range(1, 13),
        "Samsung": [13],
        "JBL": [14],
        "Apple": [15],
        "Xiaomi": [16],
        "Sony": [17],
        "Google": [18],
        "Dell": [19],
        "Logitech": [20],
    }
    for brand, product_ids in brand_updates.items():
        ids = ",".join(str(product_id) for product_id in product_ids)
        op.execute(
            sa.text(f"UPDATE products SET brand = :brand WHERE id IN ({ids})").bindparams(
                brand=brand
            )
        )

    homepage_sections = sa.table(
        "homepage_sections",
        sa.column("id", sa.Integer()),
        sa.column("section_key", sa.String()),
        sa.column("title", sa.String()),
        sa.column("subtitle", sa.Text()),
        sa.column("display_order", sa.Integer()),
        sa.column("is_active", sa.Boolean()),
    )
    op.bulk_insert(
        homepage_sections,
        [
            {
                "id": 3,
                "section_key": "product_catalog",
                "title": "Shop All Products",
                "subtitle": "Browse our extensive catalog of premium B2B grocery supplies, fresh produce, electronics, and high-margin retail products.",
                "display_order": 3,
                "is_active": True,
            }
        ],
    )

    categories_table = sa.table(
        "categories",
        sa.column("id", sa.Integer()),
        sa.column("name", sa.String()),
        sa.column("slug", sa.String()),
        sa.column("description", sa.Text()),
        sa.column("is_active", sa.Boolean()),
    )
    op.bulk_insert(
        categories_table,
        [
            {"id": 1, "name": "Fresh Fruits", "slug": "fresh-fruits", "description": "Fresh seasonal and year-round fruits.", "is_active": True},
            {"id": 2, "name": "Fresh Vegetables", "slug": "fresh-vegetables", "description": "Leafy greens, roots, and everyday vegetables.", "is_active": True},
            {"id": 3, "name": "Dairy & Eggs", "slug": "dairy-eggs", "description": "Milk, cheese, yogurt, butter, and eggs.", "is_active": True},
            {"id": 4, "name": "Bakery", "slug": "bakery", "description": "Fresh bread, pastries, cakes, and baked staples.", "is_active": True},
            {"id": 5, "name": "Meat & Seafood", "slug": "meat-seafood", "description": "Fresh and frozen meat and seafood selections.", "is_active": True},
            {"id": 6, "name": "Snacks", "slug": "snacks", "description": "Popular savory snacks, confectionery, nuts.", "is_active": True},
        ]
    )

    products_table = sa.table(
        "products",
        sa.column("id", sa.Integer()),
        sa.column("slug", sa.String()),
        sa.column("title", sa.String()),
        sa.column("brand", sa.String()),
        sa.column("short_desc", sa.Text()),
        sa.column("currency", sa.String()),
        sa.column("price", sa.Numeric()),
        sa.column("old_price", sa.Numeric()),
        sa.column("rating", sa.Numeric()),
        sa.column("sold_count", sa.Integer()),
        sa.column("badge", sa.String()),
        sa.column("is_flash_sale", sa.Boolean()),
        sa.column("display_order", sa.Integer()),
        sa.column("product_type_id", sa.Integer()),
        sa.column("category_id", sa.Integer()),
        sa.column("id_recomended", sa.Boolean()),
    )
    op.bulk_insert(products_table, _catalog_products())

    product_images_table = sa.table(
        "product_images",
        sa.column("id", sa.Integer()),
        sa.column("product_id", sa.Integer()),
        sa.column("image", sa.Text()),
        sa.column("file_type", sa.String()),
        sa.column("is_preview", sa.Boolean()),
    )
    op.bulk_insert(
        product_images_table,
        [
            {
                "id": product_id,
                "product_id": product_id,
                "image": f"/home/category-thumbnail-{((product_id - 21) // 4) + 1:02d}.png",
                "file_type": "image",
                "is_preview": True,
            }
            for product_id in range(21, 45)
        ],
    )


def downgrade() -> None:
    op.execute("DELETE FROM carts WHERE product_id BETWEEN 21 AND 44")
    op.execute("DELETE FROM product_views WHERE product_id BETWEEN 21 AND 44")
    op.execute("DELETE FROM product_images WHERE product_id BETWEEN 21 AND 44")
    op.execute("DELETE FROM products WHERE id BETWEEN 21 AND 44")
    op.execute("DELETE FROM categories WHERE id BETWEEN 1 AND 6")
    op.execute("DELETE FROM homepage_sections WHERE section_key = 'product_catalog'")
    op.drop_column("products", "brand")

