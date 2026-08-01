"""update legal brand name

Revision ID: e83b64d12fc7
Revises: d42ef59a8b16
Create Date: 2026-08-01 18:00:00
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "e83b64d12fc7"
down_revision: Union[str, Sequence[str], None] = "d42ef59a8b16"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    connection = op.get_bind()
    connection.execute(
        sa.text(
            "UPDATE footer_settings "
            "SET brand_name = :brand_name, brand_highlight = NULL, copyright_text = :copyright "
            "WHERE is_active = 1"
        ),
        {
            "brand_name": "Global Source Expo Ltd",
            "copyright": "© 2026 All rights reserved. Global Source Expo Ltd",
        },
    )
    connection.execute(
        sa.text(
            "UPDATE footer_links SET content = REPLACE(content, :old_name, :new_name) "
            "WHERE content IS NOT NULL"
        ),
        {"old_name": "Global Source Expo", "new_name": "Global Source Expo Ltd"},
    )


def downgrade() -> None:
    connection = op.get_bind()
    connection.execute(
        sa.text(
            "UPDATE footer_settings "
            "SET brand_name = :brand_name, brand_highlight = :brand_highlight, copyright_text = :copyright "
            "WHERE is_active = 1"
        ),
        {
            "brand_name": "Global",
            "brand_highlight": "Source Expo",
            "copyright": "© 2026 All rights reserved. Global Source Expo",
        },
    )
    connection.execute(
        sa.text(
            "UPDATE footer_links SET content = REPLACE(content, :new_name, :old_name) "
            "WHERE content IS NOT NULL"
        ),
        {"old_name": "Global Source Expo", "new_name": "Global Source Expo Ltd"},
    )
