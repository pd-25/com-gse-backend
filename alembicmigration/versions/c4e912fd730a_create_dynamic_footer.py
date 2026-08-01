"""create dynamic footer

Revision ID: c4e912fd730a
Revises: b97d13ac6e42
Create Date: 2026-08-01 14:35:00
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "c4e912fd730a"
down_revision: Union[str, Sequence[str], None] = "b97d13ac6e42"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "footer_settings",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("brand_name", sa.String(255), nullable=False),
        sa.Column("brand_highlight", sa.String(255), nullable=True),
        sa.Column("contact_heading", sa.String(100), nullable=False, server_default="Contact Us"),
        sa.Column("whatsapp_label", sa.String(100), nullable=False, server_default="WhatsApp"),
        sa.Column("whatsapp_number", sa.String(40), nullable=False),
        sa.Column("phone_label", sa.String(100), nullable=False, server_default="Call Us"),
        sa.Column("phone_number", sa.String(40), nullable=False),
        sa.Column("email", sa.String(255), nullable=True),
        sa.Column("connect_label", sa.String(100), nullable=False),
        sa.Column("connect_url", sa.String(500), nullable=False),
        sa.Column("store_label", sa.String(100), nullable=False),
        sa.Column("store_url", sa.String(500), nullable=False),
        sa.Column("app_heading", sa.String(100), nullable=False, server_default="Download App"),
        sa.Column("app_store_url", sa.String(500), nullable=True),
        sa.Column("app_store_badge", sa.String(500), nullable=True),
        sa.Column("play_store_url", sa.String(500), nullable=True),
        sa.Column("play_store_badge", sa.String(500), nullable=True),
        sa.Column("copyright_text", sa.String(500), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.text("1")),
    )
    op.create_table(
        "footer_links",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("section", sa.String(50), nullable=False),
        sa.Column("label", sa.String(255), nullable=False),
        sa.Column("slug", sa.String(255), nullable=True),
        sa.Column("url", sa.String(500), nullable=False),
        sa.Column("content", sa.Text(), nullable=True),
        sa.Column("sort_order", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.text("1")),
        sa.UniqueConstraint("slug", name="uq_footer_links_slug"),
    )
    op.create_index("ix_footer_links_section", "footer_links", ["section"])
    op.create_index("ix_footer_links_slug", "footer_links", ["slug"])

    settings = sa.table(
        "footer_settings",
        *[sa.column(name) for name in (
            "brand_name", "brand_highlight", "contact_heading", "whatsapp_label",
            "whatsapp_number", "phone_label", "phone_number", "email", "connect_label",
            "connect_url", "store_label", "store_url", "app_heading", "app_store_url",
            "app_store_badge", "play_store_url", "play_store_badge", "copyright_text",
        )],
    )
    op.bulk_insert(settings, [{
        "brand_name": "Global", "brand_highlight": "Source Expo", "contact_heading": "Contact Us",
        "whatsapp_label": "WhatsApp", "whatsapp_number": "+1 202-918-2132",
        "phone_label": "Call Us", "phone_number": "+1 202-918-2132",
        "email": "support@globalsourceexpo.com", "connect_label": "Connect with us",
        "connect_url": "/contact", "store_label": "Visit Our Store", "store_url": "/products",
        "app_heading": "Download App", "app_store_url": "https://www.apple.com/app-store/",
        "app_store_badge": "/app-store-badge.svg", "play_store_url": "https://play.google.com/store",
        "play_store_badge": "/google-play-badge.svg",
        "copyright_text": "© 2026 All rights reserved. Global Source Expo",
    }])

    links = sa.table(
        "footer_links",
        sa.column("section"), sa.column("label"), sa.column("slug"), sa.column("url"),
        sa.column("content"), sa.column("sort_order"),
    )
    category_rows = [
        ("Fresh Fruits", "fresh-fruits"), ("Organic Vegetables", "organic-vegetables"),
        ("Dairy Products", "dairy-products"), ("Bakery & Bread", "bakery-bread"),
        ("Meat & Seafood", "meat-seafood"), ("Snacks & Candy", "snacks-candy"),
        ("Electronics & Gadgets", "electronics-gadgets"), ("Grocery Essentials", "grocery-essentials"),
    ]
    service_rows = [
        ("About Us", "about-us", "Learn about Global Source Expo, our marketplace, and our commitment to connecting customers with dependable products and suppliers."),
        ("Terms & Conditions", "terms-conditions", "These terms describe acceptable use of our marketplace, account responsibilities, ordering, payments, and service availability."),
        ("Frequently Asked Questions", "faq", "Find answers about accounts, product discovery, ordering, delivery, payments, returns, and customer support."),
        ("Privacy Policy", "privacy-policy", "We use account and order information to provide our services, protect the marketplace, and improve customer support. We do not sell personal information."),
        ("E-waste Policy", "e-waste-policy", "Electronic products should be reused or recycled through an authorized collection partner. Do not dispose of electronics with household waste."),
        ("Cancellation & Return Policy", "cancellation-return-policy", "Eligible orders may be cancelled before dispatch. Return eligibility depends on product condition, category, and the stated return window."),
    ]
    op.bulk_insert(links, [
        {"section": "popular_category", "label": label, "slug": None,
         "url": f"/products?category={slug}", "content": None, "sort_order": index}
        for index, (label, slug) in enumerate(category_rows, 1)
    ] + [
        {"section": "customer_service", "label": label, "slug": slug,
         "url": f"/information/{slug}", "content": content, "sort_order": index}
        for index, (label, slug, content) in enumerate(service_rows, 1)
    ])


def downgrade() -> None:
    op.drop_index("ix_footer_links_slug", table_name="footer_links")
    op.drop_index("ix_footer_links_section", table_name="footer_links")
    op.drop_table("footer_links")
    op.drop_table("footer_settings")
