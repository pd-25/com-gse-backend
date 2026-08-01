"""refine product subcategory assignments

Revision ID: e62a7b30d519
Revises: d81f04ac927e
Create Date: 2026-08-01 15:20:00
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "e62a7b30d519"
down_revision: Union[str, Sequence[str], None] = "d81f04ac927e"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    connection = op.get_bind()
    names = {
        9: ("Tropical & Citrus Fruits", "Bananas, oranges, and other tropical or citrus fruit selections."),
        10: ("Berries & Grapes", "Fresh berries and grapes for retail and food service."),
        11: ("Root Vegetables", "Carrots and other nutritious root vegetables."),
        12: ("Fresh Salad Vegetables", "Tomatoes, peppers, cucumbers, and crisp salad vegetables."),
        14: ("Cheese, Butter & Eggs", "Cheese, butter, and carefully packed eggs."),
        23: ("Fresh Grocery", "Fresh produce, seafood, and chilled everyday grocery products."),
        24: ("Pantry & Breakfast", "Bread, yogurt, beverages, oils, eggs, and breakfast essentials."),
    }
    for category_id, (name, description) in names.items():
        connection.execute(
            sa.text("UPDATE categories SET name=:name, description=:description WHERE id=:id"),
            {"id": category_id, "name": name, "description": description},
        )

    assignments = {
        9: [21, 22], 10: [23, 24],
        11: [25], 12: [26, 27, 28],
        13: [29, 31], 14: [30, 32],
        15: [34, 35], 16: [33, 36],
        17: [37, 38], 18: [39, 40],
        19: [41, 42, 44], 20: [43],
        21: [13, 14, 15, 16, 17, 18], 22: [19, 20],
        23: [1, 2, 3, 8, 9, 11], 24: [4, 5, 6, 7, 10, 12],
    }
    for subcategory_id, product_ids in assignments.items():
        connection.execute(
            sa.text("UPDATE products SET subcategory_id=:subcategory_id WHERE id IN :product_ids")
            .bindparams(sa.bindparam("product_ids", expanding=True)),
            {"subcategory_id": subcategory_id, "product_ids": product_ids},
        )


def downgrade() -> None:
    op.execute(
        "UPDATE products SET subcategory_id = 9 + ((category_id - 1) * 2) + MOD(id, 2) "
        "WHERE category_id BETWEEN 1 AND 8"
    )
