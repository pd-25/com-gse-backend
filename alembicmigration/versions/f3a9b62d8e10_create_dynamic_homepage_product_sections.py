"""create dynamic homepage product sections

Revision ID: f3a9b62d8e10
Revises: d7e4f81b2c6a
Create Date: 2026-08-01 02:00:00.000000

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op


revision: str = "f3a9b62d8e10"
down_revision: Union[str, Sequence[str], None] = "d7e4f81b2c6a"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def _product_rows():
    grocery_products = [
        ("Taylor Farms Broccoli Florets", 14.99, 28.99, 4.8, 1835, "Sale 50%"),
        ("Organic Red Apples Pack", 8.49, 12.99, 4.6, 942, None),
        ("Fresh Atlantic Salmon Fillet", 22.99, 34.99, 4.9, 563, None),
        ("Whole Grain Wheat Bread", 5.49, 8.99, 4.5, 1204, "Best Sale"),
        ("Premium Greek Yogurt", 6.99, 10.99, 4.7, 876, None),
        ("Mixed Berry Smoothie Pack", 12.49, 18.99, 4.4, 421, "Sale 50%"),
        ("Farm Fresh Free Range Eggs", 7.99, 12.99, 4.8, 1567, None),
        ("Avocado Hass Premium", 3.99, 6.99, 4.3, 2103, "New"),
        ("Organic Baby Spinach Leaves", 4.49, 7.49, 4.6, 734, None),
        ("Italian Extra Virgin Olive Oil", 18.99, 26.99, 4.9, 398, "Best Sale"),
        ("Wild Caught Tuna Steaks", 24.99, 32.99, 4.7, 612, None),
        ("Artisan Sourdough Loaf", 6.49, 9.99, 4.5, 1089, None),
    ]
    electronics_products = [
        ("Samsung Galaxy M13 (4GB)", 104.99, 149.99, 4.5, 2340, "Sale 30%"),
        ("JBL Tune 520BT Headphone", 34.99, 59.99, 4.3, 1567, None),
        ("Apple AirPods Pro 2nd Gen", 249.99, 299.99, 4.8, 891, None),
        ("Xiaomi Smart Band 8 Pro", 49.99, 69.99, 4.2, 3201, "Best Sale"),
        ("Sony WH-1000XM5 Wireless", 299.99, 349.99, 4.9, 432, None),
        ("Google Pixel Buds Pro", 199.99, 229.99, 4.6, 765, None),
        ("Dell Inspiron 15 Laptop", 549.99, 699.99, 4.4, 234, "New"),
        ("Logitech MX Master 3S", 89.99, 119.99, 4.7, 1890, None),
    ]

    rows = []
    for index, (title, price, old_price, rating, sold_count, badge) in enumerate(
        grocery_products, start=1
    ):
        rows.append(
            {
                "id": index,
                "slug": title.lower().replace("&", "and").replace(" ", "-").replace("(", "").replace(")", ""),
                "title": title,
                "short_desc": "Fresh quality product selected for today’s flash sale.",
                "currency": "USD",
                "price": price,
                "old_price": old_price,
                "rating": rating,
                "sold_count": sold_count,
                "badge": badge,
                "is_flash_sale": True,
                "display_order": index,
                "product_type_id": 1,
                "category_id": 8,
                "id_recomended": True,
            }
        )

    for offset, (title, price, old_price, rating, sold_count, badge) in enumerate(
        electronics_products, start=1
    ):
        product_id = 12 + offset
        rows.append(
            {
                "id": product_id,
                "slug": title.lower().replace("&", "and").replace(" ", "-").replace("(", "").replace(")", ""),
                "title": title,
                "short_desc": "Popular electronics product from a verified supplier.",
                "currency": "USD",
                "price": price,
                "old_price": old_price,
                "rating": rating,
                "sold_count": sold_count,
                "badge": badge,
                "is_flash_sale": False,
                "display_order": offset,
                "product_type_id": 2,
                "category_id": 7,
                "id_recomended": True,
            }
        )
    return rows


def upgrade() -> None:
    op.add_column("products", sa.Column("old_price", sa.Numeric(10, 2), nullable=True))
    op.add_column("products", sa.Column("rating", sa.Numeric(2, 1), nullable=True))
    op.add_column("products", sa.Column("sold_count", sa.Integer(), server_default="0", nullable=False))
    op.add_column("products", sa.Column("badge", sa.String(100), nullable=True))
    op.add_column("products", sa.Column("is_flash_sale", sa.Boolean(), server_default="0", nullable=False))
    op.add_column("products", sa.Column("display_order", sa.Integer(), server_default="0", nullable=False))

    op.add_column("categories", sa.Column("showcase_image", sa.Text(), nullable=True))
    op.add_column("categories", sa.Column("showcase_tag", sa.String(100), nullable=True))
    op.add_column("categories", sa.Column("showcase_description", sa.String(255), nullable=True))
    op.add_column("categories", sa.Column("showcase_button_text", sa.String(100), nullable=True))
    op.add_column("categories", sa.Column("showcase_button_url", sa.String(500), nullable=True))
    op.add_column("categories", sa.Column("is_showcase", sa.Boolean(), server_default="0", nullable=False))
    op.add_column("categories", sa.Column("display_order", sa.Integer(), server_default="0", nullable=False))

    homepage_sections = op.create_table(
        "homepage_sections",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("section_key", sa.String(100), nullable=False),
        sa.Column("title", sa.String(255), nullable=False),
        sa.Column("subtitle", sa.Text(), nullable=True),
        sa.Column("display_order", sa.Integer(), server_default="0", nullable=False),
        sa.Column("is_active", sa.Boolean(), server_default="1", nullable=False),
        sa.Column("created_at", sa.DateTime(), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=True),
        sa.Column(
            "updated_at",
            sa.DateTime(),
            server_default=sa.text("CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP"),
            nullable=True,
        ),
        sa.Column("deleted_at", sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_homepage_sections_section_key", "homepage_sections", ["section_key"], unique=True)

    op.bulk_insert(
        homepage_sections,
        [
            {
                "id": 1,
                "section_key": "flash_sales",
                "title": "Flash Sales Today",
                "subtitle": "Limited time offers — grab them before they’re gone",
                "display_order": 1,
                "is_active": True,
            },
            {
                "id": 2,
                "section_key": "category_showcases",
                "title": "Browse by Product Category",
                "subtitle": "Discover quality products across our top-selling categories",
                "display_order": 2,
                "is_active": True,
            },
        ],
    )

    product_types_table = sa.table(
        "product_types",
        sa.column("id", sa.Integer()),
        sa.column("name", sa.String()),
    )
    op.bulk_insert(
        product_types_table,
        [{"id": 1, "name": "Food & Beverages"}, {"id": 2, "name": "Electronics"}],
    )

    categories_table = sa.table(
        "categories",
        sa.column("id", sa.Integer()),
        sa.column("name", sa.String()),
        sa.column("slug", sa.String()),
        sa.column("description", sa.Text()),
        sa.column("image", sa.Text()),
        sa.column("showcase_image", sa.Text()),
        sa.column("showcase_tag", sa.String()),
        sa.column("showcase_description", sa.String()),
        sa.column("showcase_button_text", sa.String()),
        sa.column("showcase_button_url", sa.String()),
        sa.column("is_showcase", sa.Boolean()),
        sa.column("display_order", sa.Integer()),
        sa.column("is_active", sa.Boolean()),
    )
    op.bulk_insert(
        categories_table,
        [
            {
                "id": 7,
                "name": "Electronics & Gadgets",
                "slug": "electronics-gadgets",
                "description": "Phones, audio, wearables, laptops, and accessories.",
                "image": "/home/featured-product-thumbnail.webp",
                "showcase_image": "/home/featured-product-thumbnail.webp",
                "showcase_tag": "Trending",
                "showcase_description": "Popular technology products from verified suppliers",
                "showcase_button_text": "Source Now",
                "showcase_button_url": "/products?category=electronics-gadgets",
                "is_showcase": True,
                "display_order": 1,
                "is_active": True,
            },
            {
                "id": 8,
                "name": "Grocery Essentials",
                "slug": "grocery-essentials",
                "description": "Fresh food and pantry essentials for everyday business needs.",
                "image": "/sample-image.png",
                "showcase_image": "https://html.themewant.com/ekomart/assets/images/banner/08.webp",
                "showcase_tag": "Fresh Deals",
                "showcase_description": "Fresh grocery products available for wholesale orders",
                "showcase_button_text": "Shop Now",
                "showcase_button_url": "/products?category=grocery-essentials",
                "is_showcase": True,
                "display_order": 2,
                "is_active": True,
            },
        ],
    )

    products_table = sa.table(
        "products",
        sa.column("id", sa.Integer()),
        sa.column("slug", sa.String()),
        sa.column("title", sa.String()),
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
    op.bulk_insert(products_table, _product_rows())

    product_images_table = sa.table(
        "product_images",
        sa.column("id", sa.Integer()),
        sa.column("product_id", sa.Integer()),
        sa.column("image", sa.Text()),
        sa.column("file_type", sa.String()),
        sa.column("is_preview", sa.Boolean()),
    )
    image_rows = [
        {
            "id": product_id,
            "product_id": product_id,
            "image": "/sample-image.png" if product_id <= 12 else f"/home/prod{product_id - 12}.jpeg",
            "file_type": "image",
            "is_preview": True,
        }
        for product_id in range(1, 21)
    ]
    op.bulk_insert(product_images_table, image_rows)


def downgrade() -> None:
    op.execute("DELETE FROM carts WHERE product_id BETWEEN 1 AND 20")
    op.execute("DELETE FROM product_views WHERE product_id BETWEEN 1 AND 20")
    op.execute("DELETE FROM product_images WHERE product_id BETWEEN 1 AND 20")
    op.execute("DELETE FROM products WHERE id BETWEEN 1 AND 20")
    op.execute("DELETE FROM categories WHERE id IN (7, 8)")
    op.execute("DELETE FROM product_types WHERE id IN (1, 2)")

    op.drop_index("ix_homepage_sections_section_key", table_name="homepage_sections")
    op.drop_table("homepage_sections")

    op.drop_column("categories", "display_order")
    op.drop_column("categories", "is_showcase")
    op.drop_column("categories", "showcase_button_url")
    op.drop_column("categories", "showcase_button_text")
    op.drop_column("categories", "showcase_description")
    op.drop_column("categories", "showcase_tag")
    op.drop_column("categories", "showcase_image")

    op.drop_column("products", "display_order")
    op.drop_column("products", "is_flash_sale")
    op.drop_column("products", "badge")
    op.drop_column("products", "sold_count")
    op.drop_column("products", "rating")
    op.drop_column("products", "old_price")
