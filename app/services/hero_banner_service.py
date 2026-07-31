from sqlalchemy.orm import Session

from app.models.hero_banner import HeroBanner
from app.schemas.hero_banner_schema import HeroBannerFilterSchema, HeroBannerListResponse


def fetch_hero_banners(filters: HeroBannerFilterSchema, db: Session):
    limit = max(1, min(filters.limit, 50))
    banners = (
        db.query(HeroBanner)
        .filter(
            HeroBanner.is_active.is_(True),
            HeroBanner.deleted_at.is_(None),
        )
        .order_by(HeroBanner.display_order, HeroBanner.id)
        .limit(limit)
        .all()
    )
    return [HeroBannerListResponse.model_validate(banner, from_attributes=True) for banner in banners]
