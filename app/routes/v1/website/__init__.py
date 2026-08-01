from fastapi import APIRouter

from app.routes.v1.website.category_route import category_router
from app.routes.v1.website.promotional_card_route import promotional_card_router
from app.routes.v1.website.hero_banner_route import hero_banner_router
from app.routes.v1.website.homepage_product_route import homepage_product_router
from app.routes.v1.website.catalog_route import catalog_router
from app.routes.v1.website.auth_route import auth_router
from app.routes.v1.website.footer_route import footer_router
from app.routes.v1.website.payment_route import payment_router


website_router = APIRouter()

website_router.include_router(category_router, prefix="/categories", tags=["Website - Category"])
website_router.include_router(
    promotional_card_router,
    prefix="/promotional-cards",
    tags=["Website - Promotional Cards"],
)
website_router.include_router(
    hero_banner_router,
    prefix="/hero-banners",
    tags=["Website - Hero Banners"],
)
website_router.include_router(
    homepage_product_router,
    prefix="/homepage",
    tags=["Website - Homepage Products"],
)
website_router.include_router(
    catalog_router,
    prefix="/catalog",
    tags=["Website - Product Catalog"],
)
website_router.include_router(
    auth_router,
    prefix="/auth",
    tags=["Website - Authentication"],
)
website_router.include_router(
    footer_router,
    prefix="/footer",
    tags=["Website - Footer"],
)
website_router.include_router(
    payment_router,
    prefix="/payments",
    tags=["Website - Payments & Bookings"],
)
