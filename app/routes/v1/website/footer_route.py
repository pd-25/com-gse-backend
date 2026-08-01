from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.schemas.footer_schema import FooterPageResponse, FooterResponse
from app.schemas.response import APIResponse
from app.services.footer_service import fetch_footer, fetch_footer_page


footer_router = APIRouter()


@footer_router.get("/", response_model=APIResponse[FooterResponse])
def get_footer(db: Session = Depends(get_db)):
    return APIResponse(
        success=True,
        message="Footer fetched successfully",
        data=fetch_footer(db),
        meta={},
    )


@footer_router.get("/pages/{slug}/", response_model=APIResponse[FooterPageResponse])
def get_footer_page(slug: str, db: Session = Depends(get_db)):
    return APIResponse(
        success=True,
        message="Information page fetched successfully",
        data=fetch_footer_page(slug=slug, db=db),
        meta={},
    )
