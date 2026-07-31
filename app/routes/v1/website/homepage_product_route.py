from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.schemas.homepage_product_schema import (
    CategoryShowcaseFilterSchema,
    CategoryShowcaseSectionResponse,
    FlashSaleFilterSchema,
    FlashSaleSectionResponse,
)
from app.schemas.response import APIResponse
from app.services.homepage_product_service import (
    fetch_category_showcase_section,
    fetch_flash_sale_section,
)


homepage_product_router = APIRouter()


@homepage_product_router.get(
    "/flash-sales/",
    response_model=APIResponse[FlashSaleSectionResponse],
)
def get_flash_sales(
    filters: FlashSaleFilterSchema = Depends(),
    db: Session = Depends(get_db),
):
    return APIResponse(
        success=True,
        message="Flash sale section fetched successfully",
        data=fetch_flash_sale_section(filters=filters, db=db),
        meta={},
    )


@homepage_product_router.get(
    "/category-showcases/",
    response_model=APIResponse[CategoryShowcaseSectionResponse],
)
def get_category_showcases(
    filters: CategoryShowcaseFilterSchema = Depends(),
    db: Session = Depends(get_db),
):
    return APIResponse(
        success=True,
        message="Category showcase section fetched successfully",
        data=fetch_category_showcase_section(filters=filters, db=db),
        meta={},
    )
