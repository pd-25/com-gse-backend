"""add SSLCommerz payment fields

Revision ID: 2a7f41c9d620
Revises: e83b64d12fc7
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "2a7f41c9d620"
down_revision: Union[str, Sequence[str], None] = "e83b64d12fc7"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("orders", sa.Column("payment_provider", sa.String(30), nullable=False, server_default="razorpay"))
    op.add_column("orders", sa.Column("sslcommerz_transaction_id", sa.String(100), nullable=True))
    op.add_column("orders", sa.Column("sslcommerz_session_key", sa.String(255), nullable=True))
    op.add_column("orders", sa.Column("sslcommerz_validation_id", sa.String(100), nullable=True))
    op.add_column("orders", sa.Column("sslcommerz_bank_transaction_id", sa.String(100), nullable=True))
    op.add_column("orders", sa.Column("sslcommerz_card_type", sa.String(100), nullable=True))
    op.create_index("ix_orders_sslcommerz_transaction_id", "orders", ["sslcommerz_transaction_id"], unique=True)
    op.create_unique_constraint("uq_orders_sslcommerz_session_key", "orders", ["sslcommerz_session_key"])
    op.create_unique_constraint("uq_orders_sslcommerz_validation_id", "orders", ["sslcommerz_validation_id"])


def downgrade() -> None:
    op.drop_constraint("uq_orders_sslcommerz_validation_id", "orders", type_="unique")
    op.drop_constraint("uq_orders_sslcommerz_session_key", "orders", type_="unique")
    op.drop_index("ix_orders_sslcommerz_transaction_id", table_name="orders")
    op.drop_column("orders", "sslcommerz_card_type")
    op.drop_column("orders", "sslcommerz_bank_transaction_id")
    op.drop_column("orders", "sslcommerz_validation_id")
    op.drop_column("orders", "sslcommerz_session_key")
    op.drop_column("orders", "sslcommerz_transaction_id")
    op.drop_column("orders", "payment_provider")
