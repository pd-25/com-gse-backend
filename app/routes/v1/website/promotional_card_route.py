from typing import List

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.schemas.promotional_card_schema import (
    PromotionalCardFilterSchema,
    PromotionalCardListResponse,
)
from app.schemas.response import APIResponse
from app.services.promotional_card_service import fetch_promotional_cards


promotional_card_router = APIRouter()


@promotional_card_router.get(
    "/", response_model=APIResponse[List[PromotionalCardListResponse]]
)
def get_promotional_cards(
    filters: PromotionalCardFilterSchema = Depends(),
    db: Session = Depends(get_db),
):
    cards = fetch_promotional_cards(filters=filters, db=db)
    return APIResponse(
        success=True,
        message="Promotional cards fetched successfully",
        data=cards,
        meta={},
    )
