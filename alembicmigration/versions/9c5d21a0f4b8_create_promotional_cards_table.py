"""create promotional cards table

Revision ID: 9c5d21a0f4b8
Revises: bc4aee50ccb7
Create Date: 2026-08-01 00:00:00.000000

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op


revision: str = "9c5d21a0f4b8"
down_revision: Union[str, Sequence[str], None] = "bc4aee50ccb7"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    promotional_cards = op.create_table(
        "promotional_cards",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("title", sa.String(length=255), nullable=False),
        sa.Column("price", sa.Numeric(precision=10, scale=2), nullable=False),
        sa.Column("currency", sa.String(length=3), server_default="USD", nullable=False),
        sa.Column("image", sa.Text(), nullable=False),
        sa.Column("button_text", sa.String(length=100), server_default="Shop Now", nullable=False),
        sa.Column("button_url", sa.String(length=500), server_default="/products", nullable=False),
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

    op.bulk_insert(
        promotional_cards,
        [
            {
                "id": card_id,
                "title": "Everyday Fresh Meat",
                "price": 90.52,
                "currency": "USD",
                "image": "/home/top-brand-thumbnail.png",
                "button_text": "Shop Now",
                "button_url": "/products",
                "display_order": card_id,
                "is_active": True,
            }
            for card_id in range(1, 5)
        ],
    )


def downgrade() -> None:
    op.drop_table("promotional_cards")
