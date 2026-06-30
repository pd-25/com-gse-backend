from fastapi import APIRouter

from app.routes.v1.website.category_route import category_router


website_router = APIRouter()

website_router.include_router(category_router, prefix="/categories", tags=["Website - Category"])