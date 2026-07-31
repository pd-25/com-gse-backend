from typing import List

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.schemas.hero_banner_schema import HeroBannerFilterSchema, HeroBannerListResponse
from app.schemas.response import APIResponse
from app.services.hero_banner_service import fetch_hero_banners


hero_banner_router = APIRouter()


@hero_banner_router.get("/", response_model=APIResponse[List[HeroBannerListResponse]])
def get_hero_banners(
    filters: HeroBannerFilterSchema = Depends(),
    db: Session = Depends(get_db),
):
    banners = fetch_hero_banners(filters=filters, db=db)
    return APIResponse(
        success=True,
        message="Hero banners fetched successfully",
        data=banners,
        meta={},
    )
