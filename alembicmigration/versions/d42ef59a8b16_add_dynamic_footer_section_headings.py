"""add dynamic footer section headings

Revision ID: d42ef59a8b16
Revises: ab71e849c203
Create Date: 2026-08-01 17:10:00
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "d42ef59a8b16"
down_revision: Union[str, Sequence[str], None] = "ab71e849c203"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "footer_settings",
        sa.Column(
            "popular_categories_heading",
            sa.String(100),
            nullable=False,
            server_default="Most Popular Categories",
        ),
    )
    op.add_column(
        "footer_settings",
        sa.Column(
            "customer_services_heading",
            sa.String(100),
            nullable=False,
            server_default="Customer Services",
        ),
    )


def downgrade() -> None:
    op.drop_column("footer_settings", "customer_services_heading")
    op.drop_column("footer_settings", "popular_categories_heading")
