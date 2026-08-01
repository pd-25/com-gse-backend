from typing import List

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.schemas.category_schema import CategoryDetailResponse, CategoryFilterSchema, CategoryListResponse
from app.schemas.response import APIResponse
from app.services.category_service import fetch_categories, fetch_category_detail

category_router = APIRouter()


@category_router.get('/', response_model=APIResponse[List[CategoryListResponse]])
def get_categories(filters: CategoryFilterSchema = Depends(), db: Session = Depends(get_db)):
    categories = fetch_categories(filters=filters, db=db)
    return APIResponse(
        success=True,
        message="Category Wise Subcategories Fetched Successfully",
        data=categories,
        meta={},
    )


@category_router.get('/{slug}/', response_model=APIResponse[CategoryDetailResponse])
def get_category_detail(slug: str, db: Session = Depends(get_db)):
    return APIResponse(
        success=True,
        message="Category details fetched successfully",
        data=fetch_category_detail(slug=slug, db=db),
        meta={},
    )
