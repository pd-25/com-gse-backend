from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.schemas.catalog_schema import (
    CatalogFacetsResponse,
    CatalogFilterSchema,
    CatalogProductResponse,
    SearchSuggestionFilterSchema,
    SearchSuggestionResponse,
)
from app.schemas.response import APIResponse
from app.services.catalog_service import (
    fetch_catalog_facets,
    fetch_catalog_product_by_slug,
    fetch_catalog_products,
    fetch_search_suggestions,
)


catalog_router = APIRouter()


@catalog_router.get("/products/", response_model=APIResponse[List[CatalogProductResponse]])
def get_catalog_products(
    filters: CatalogFilterSchema = Depends(),
    db: Session = Depends(get_db),
):
    products, meta = fetch_catalog_products(filters=filters, db=db)
    return APIResponse(
        success=True,
        message="Catalog products fetched successfully",
        data=products,
        meta=meta,
    )


@catalog_router.get(
    "/products/{slug}/",
    response_model=APIResponse[CatalogProductResponse],
)
def get_catalog_product(slug: str, db: Session = Depends(get_db)):
    product = fetch_catalog_product_by_slug(slug=slug, db=db)
    if product is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found",
        )
    return APIResponse(
        success=True,
        message="Catalog product fetched successfully",
        data=product,
        meta={},
    )


@catalog_router.get("/filters/", response_model=APIResponse[CatalogFacetsResponse])
def get_catalog_filters(db: Session = Depends(get_db)):
    return APIResponse(
        success=True,
        message="Catalog filters fetched successfully",
        data=fetch_catalog_facets(db),
        meta={},
    )


@catalog_router.get(
    "/search-suggestions/",
    response_model=APIResponse[List[SearchSuggestionResponse]],
)
def get_search_suggestions(
    filters: SearchSuggestionFilterSchema = Depends(),
    db: Session = Depends(get_db),
):
    return APIResponse(
        success=True,
        message="Search suggestions fetched successfully",
        data=fetch_search_suggestions(filters=filters, db=db),
        meta={},
    )
