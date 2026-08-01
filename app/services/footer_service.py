from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.footer_setting import FooterLink, FooterSetting
from app.schemas.footer_schema import FooterPageResponse, FooterResponse


def fetch_footer(db: Session) -> FooterResponse:
    settings = (
        db.query(FooterSetting)
        .filter(FooterSetting.is_active.is_(True))
        .order_by(FooterSetting.id.desc())
        .first()
    )
    if settings is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Footer configuration not found",
        )

    links = (
        db.query(FooterLink)
        .filter(FooterLink.is_active.is_(True))
        .order_by(FooterLink.section, FooterLink.sort_order, FooterLink.id)
        .all()
    )
    return FooterResponse(
        settings=settings,
        popular_categories_heading=settings.popular_categories_heading,
        customer_services_heading=settings.customer_services_heading,
        popular_categories=[link for link in links if link.section == "popular_category"],
        customer_services=[link for link in links if link.section == "customer_service"],
    )


def fetch_footer_page(slug: str, db: Session) -> FooterPageResponse:
    page = (
        db.query(FooterLink)
        .filter(
            FooterLink.section == "customer_service",
            FooterLink.slug == slug,
            FooterLink.is_active.is_(True),
        )
        .first()
    )
    if page is None or not page.content:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Information page not found")
    return FooterPageResponse(title=page.label, slug=page.slug, content=page.content)
