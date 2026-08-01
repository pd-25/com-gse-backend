"""seed default registration country

Revision ID: b97d13ac6e42
Revises: a8c4e20f6b91
Create Date: 2026-08-01 14:00:00
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "b97d13ac6e42"
down_revision: Union[str, Sequence[str], None] = "a8c4e20f6b91"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    countries = sa.table(
        "countries",
        sa.column("name", sa.String),
        sa.column("country_code", sa.String),
        sa.column("dial_code", sa.String),
        sa.column("country_flag", sa.Text),
    )
    connection = op.get_bind()
    exists = connection.execute(
        sa.text("SELECT id FROM countries WHERE country_code = :code LIMIT 1"),
        {"code": "IN"},
    ).first()
    if exists is None:
        op.bulk_insert(
            countries,
            [{"name": "India", "country_code": "IN", "dial_code": "+91", "country_flag": "🇮🇳"}],
        )


def downgrade() -> None:
    op.execute(sa.text("DELETE FROM countries WHERE country_code = 'IN'"))
