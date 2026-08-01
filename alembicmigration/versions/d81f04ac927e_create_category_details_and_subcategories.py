"""create category details and subcategories

Revision ID: d81f04ac927e
Revises: c4e912fd730a
Create Date: 2026-08-01 15:00:00
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "d81f04ac927e"
down_revision: Union[str, Sequence[str], None] = "c4e912fd730a"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("categories", sa.Column("quality_standards", sa.Text(), nullable=True))
    op.add_column("categories", sa.Column("buying_guide", sa.Text(), nullable=True))
    op.add_column("products", sa.Column("subcategory_id", sa.Integer(), nullable=True))
    op.create_foreign_key(
        "fk_products_subcategory_id_categories",
        "products", "categories", ["subcategory_id"], ["id"],
    )
    op.create_index("ix_products_subcategory_id", "products", ["subcategory_id"])

    connection = op.get_bind()
    parent_details = {
        1: ("Fresh seasonal and year-round fruits sourced for retail, hospitality, and wholesale buyers.", "Selected for freshness, appearance, maturity, and careful handling throughout the supply chain.", "Compare origin, grade, ripeness, pack size, minimum order, and delivery time before ordering."),
        2: ("A broad selection of leafy greens, roots, and everyday vegetables for commercial kitchens and retailers.", "Produce is checked for freshness, cleanliness, uniform size, and responsible growing practices.", "Choose by harvest date, farming method, pack size, shelf life, and intended preparation."),
        3: ("Milk, cheese, yogurt, butter, and eggs supplied with dependable cold-chain handling.", "Quality focuses on temperature control, freshness, sealed packaging, and clearly marked expiry information.", "Review fat content, storage temperature, shelf life, pack size, and dietary requirements."),
        4: ("Fresh bread, pastries, cakes, and baked staples for cafes, stores, and food-service buyers.", "Products are evaluated for ingredient quality, consistent texture, freshness, and hygienic packaging.", "Check bake date, ingredients, allergens, unit size, shelf life, and storage instructions."),
        5: ("Fresh and frozen meat and seafood selections prepared for wholesale and food-service requirements.", "Standards cover cold-chain integrity, cut consistency, hygiene, traceability, and secure packaging.", "Compare cut, grade, origin, frozen or fresh condition, weight, and delivery temperature."),
        6: ("Popular savory snacks, confectionery, nuts, and convenient treats for retail inventory.", "Products use sealed packaging, clear ingredient labels, consistent portioning, and valid shelf-life controls.", "Review flavor, allergens, case quantity, unit size, expiry window, and retail margin."),
        7: ("Phones, computers, audio, accessories, and smart devices from recognizable technology brands.", "Quality indicators include specification accuracy, warranty coverage, condition, compatibility, and supplier support.", "Compare model, technical specifications, warranty, included accessories, compatibility, and after-sales support."),
        8: ("Everyday pantry, cooking, beverage, and household essentials for businesses and families.", "Products are selected for dependable packaging, consistent quality, clear labeling, and value.", "Compare brand, pack size, unit price, shelf life, ingredients, and minimum order quantity."),
    }
    for category_id, values in parent_details.items():
        connection.execute(
            sa.text("UPDATE categories SET description=:description, quality_standards=:quality, buying_guide=:guide WHERE id=:id"),
            {"id": category_id, "description": values[0], "quality": values[1], "guide": values[2]},
        )

    categories = sa.table(
        "categories",
        sa.column("id"), sa.column("name"), sa.column("slug"), sa.column("description"),
        sa.column("quality_standards"), sa.column("buying_guide"), sa.column("image"),
        sa.column("thumbnail_image"), sa.column("parent_id"), sa.column("display_order"),
        sa.column("is_active"),
    )
    rows = [
        (9, 1, "Citrus Fruits", "citrus-fruits", "Oranges, lemons, and other fresh citrus varieties."),
        (10, 1, "Berries & Cherries", "berries-cherries", "Fresh berries and cherries for retail and food service."),
        (11, 2, "Leafy Greens", "leafy-greens", "Spinach, lettuce, kale, and other fresh greens."),
        (12, 2, "Root Vegetables", "root-vegetables", "Potatoes, carrots, beets, and nutritious root vegetables."),
        (13, 3, "Milk & Yogurt", "milk-yogurt", "Chilled milk and cultured dairy products."),
        (14, 3, "Cheese & Eggs", "cheese-eggs", "Cheese selections and carefully packed eggs."),
        (15, 4, "Bread & Rolls", "bread-rolls", "Fresh loaves, buns, rolls, and everyday bakery staples."),
        (16, 4, "Cakes & Pastries", "cakes-pastries", "Sweet baked goods for stores, cafes, and events."),
        (17, 5, "Fresh Meat", "fresh-meat", "Selected poultry and meat cuts in secure packaging."),
        (18, 5, "Fish & Seafood", "fish-seafood", "Fresh and frozen fish, shellfish, and seafood."),
        (19, 6, "Chips & Savory Snacks", "chips-savory-snacks", "Popular packaged chips, crackers, and savory snacks."),
        (20, 6, "Chocolate & Candy", "chocolate-candy", "Chocolate, candy, and confectionery for retail."),
        (21, 7, "Mobiles & Wearables", "mobiles-wearables", "Smartphones, watches, earbuds, and personal devices."),
        (22, 7, "Computers & Accessories", "computers-accessories", "Laptops, input devices, and computing accessories."),
        (23, 8, "Pantry Staples", "pantry-staples", "Grains, oils, spices, and essential cooking ingredients."),
        (24, 8, "Beverages & Breakfast", "beverages-breakfast", "Tea, coffee, cereals, and convenient breakfast products."),
    ]
    image_by_parent = {
        1: "/home/category-thumbnail-01.png", 2: "/home/category-thumbnail-02.png",
        3: "/home/category-thumbnail-03.png", 4: "/home/category-thumbnail-04.png",
        5: "/home/category-thumbnail-05.png", 6: "/home/category-thumbnail-06.png",
        7: "/home/featured-product-thumbnail.webp", 8: "/sample-image.png",
    }
    op.bulk_insert(categories, [{
        "id": row[0], "parent_id": row[1], "name": row[2], "slug": row[3],
        "description": row[4], "quality_standards": "Verified product information, secure packaging, and consistent supplier quality.",
        "buying_guide": "Compare specifications, pricing, minimum order, ratings, and delivery terms.",
        "image": image_by_parent[row[1]], "thumbnail_image": image_by_parent[row[1]],
        "display_order": index % 2 + 1, "is_active": True,
    } for index, row in enumerate(rows)])

    connection.execute(sa.text(
        "UPDATE products SET subcategory_id = 9 + ((category_id - 1) * 2) + MOD(id, 2) "
        "WHERE category_id BETWEEN 1 AND 8"
    ))


def downgrade() -> None:
    op.drop_index("ix_products_subcategory_id", table_name="products")
    op.drop_constraint("fk_products_subcategory_id_categories", "products", type_="foreignkey")
    op.drop_column("products", "subcategory_id")
    op.execute("DELETE FROM categories WHERE id BETWEEN 9 AND 24")
    op.drop_column("categories", "buying_guide")
    op.drop_column("categories", "quality_standards")
