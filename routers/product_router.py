"""
routers/product_router.py

Read-only product catalog endpoints. Delegates entirely to
services/product_service.py - no SQL here.
"""

from fastapi import APIRouter, status

from schemas.responses import StandardResponse
from services import product_service
from routers.common import run_service

router = APIRouter(tags=["Products"])


@router.get("/products", response_model=StandardResponse, status_code=status.HTTP_200_OK)
def get_products():
    """List every product in the catalog."""
    return run_service(product_service.get_all_products)


@router.get("/products/search", response_model=StandardResponse, status_code=status.HTTP_200_OK)
def search_products(keyword: str):
    """Search products by a name/description keyword."""
    return run_service(product_service.search_product, keyword)


@router.get("/products/category/{category}", response_model=StandardResponse, status_code=status.HTTP_200_OK)
def get_products_by_category(category: str):
    """List products belonging to a category."""
    return run_service(product_service.search_by_category, category)


@router.get("/products/{product_id}", response_model=StandardResponse, status_code=status.HTTP_200_OK)
def get_product(product_id: str):
    """Fetch a single product by id."""
    return run_service(product_service.get_product_by_id, product_id)


@router.get("/best-sellers", response_model=StandardResponse, status_code=status.HTTP_200_OK)
def best_sellers():
    """List top-selling products."""
    return run_service(product_service.get_best_sellers)


@router.get("/new-arrivals", response_model=StandardResponse, status_code=status.HTTP_200_OK)
def new_arrivals():
    """List the most recently added products."""
    return run_service(product_service.get_new_arrivals)


@router.get("/deals", response_model=StandardResponse, status_code=status.HTTP_200_OK)
def deals():
    """List currently discounted products."""
    return run_service(product_service.get_discounted_products)