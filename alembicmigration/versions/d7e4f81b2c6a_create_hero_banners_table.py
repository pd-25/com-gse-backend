"""create hero banners table

Revision ID: d7e4f81b2c6a
Revises: 9c5d21a0f4b8
Create Date: 2026-08-01 01:00:00.000000

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op


revision: str = "d7e4f81b2c6a"
down_revision: Union[str, Sequence[str], None] = "9c5d21a0f4b8"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    hero_banners = op.create_table(
        "hero_banners",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("title", sa.String(length=255), nullable=False),
        sa.Column("subtitle", sa.String(length=255), nullable=True),
        sa.Column("price", sa.Numeric(precision=10, scale=2), nullable=True),
        sa.Column("currency", sa.String(length=3), server_default="USD", nullable=False),
        sa.Column("image", sa.Text(), nullable=False),
        sa.Column("button_text", sa.String(length=100), server_default="Explore Shop", nullable=False),
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
        hero_banners,
        [
            {
                "id": 1,
                "title": "Daily Grocery Order and Get Express Delivery",
                "subtitle": "Save Up To 50% Off On Your First Order",
                "price": 60.99,
                "currency": "USD",
                "image": "https://html.themewant.com/ekomart/assets/images/banner/08.webp",
                "button_text": "Explore Shop",
                "button_url": "/products",
                "display_order": 1,
                "is_active": True,
            },
            {
                "id": 2,
                "title": "The leading B2B marketplace for European trade",
                "subtitle": "Post your request to verified suppliers.",
                "price": 60.99,
                "currency": "USD",
                "image": "https://images.prismic.io/jamcart/13378c49-bdb1-431a-9dff-48571297347d_minimal-banner-image.png?auto=compress,format",
                "button_text": "Explore Shop",
                "button_url": "/products",
                "display_order": 2,
                "is_active": True,
            },
        ],
    )


def downgrade() -> None:
    op.drop_table("hero_banners")
