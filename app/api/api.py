from __future__ import annotations

from fastapi import APIRouter

from utils.routers import remove_trailing_slashes as clean

from .routers import (
    auth_router,
    brands_router,
    categories_router,
    common_router,
    products_router,
    sellers_router,
    suppliers_router,
    users_router,
)


def create_api_router() -> APIRouter:
    api_router = APIRouter()
    api_router.include_router(clean(auth_router), prefix="/auth")
    api_router.include_router(clean(common_router), prefix="/common")
    api_router.include_router(clean(users_router), prefix="/users")
    api_router.include_router(clean(sellers_router), prefix="/sellers")
    api_router.include_router(clean(suppliers_router), prefix="/suppliers")
    api_router.include_router(clean(categories_router), prefix="/categories")
    api_router.include_router(clean(products_router), prefix="/products")
    api_router.include_router(clean(brands_router), prefix="/brands")

    return api_router


router = create_api_router()
