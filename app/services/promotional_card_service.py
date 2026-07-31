from sqlalchemy.orm import Session

from app.models.promotional_card import PromotionalCard
from app.schemas.promotional_card_schema import (
    PromotionalCardFilterSchema,
    PromotionalCardListResponse,
)


def fetch_promotional_cards(filters: PromotionalCardFilterSchema, db: Session):
    limit = max(1, min(filters.limit, 50))
    cards = (
        db.query(PromotionalCard)
        .filter(
            PromotionalCard.is_active.is_(True),
            PromotionalCard.deleted_at.is_(None),
        )
        .order_by(PromotionalCard.display_order, PromotionalCard.id)
        .limit(limit)
        .all()
    )
    return [PromotionalCardListResponse.model_validate(card, from_attributes=True) for card in cards]
