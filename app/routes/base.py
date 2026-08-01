from fastapi import APIRouter
from app.routes.v1.website import website_router
from app.routes.v1.admin_route import admin_router

api_router = APIRouter()

api_router.include_router(website_router, prefix="/api/v1/web")
api_router.include_router(admin_router, prefix="/api/v1/admin", tags=["Admin"])
