from __future__ import annotations

from fastapi import APIRouter

from .routers import (
    auth_router,
    categories_router,
    common_router,
    password_router,
    products_router,
    register_router,
    reviews_router,
    sellers_router,
    suppliers_router,
    users_router,
)


def create_api_router() -> APIRouter:
    api_router = APIRouter()
    api_router.include_router(auth_router, tags=["auth"], prefix="/auth")
    api_router.include_router(categories_router, tags=["categories"], prefix="/categories")
    api_router.include_router(common_router, tags=["common"], prefix="/common")
    api_router.include_router(password_router, tags=["password"], prefix="/password")
    api_router.include_router(products_router, tags=["products"], prefix="/products")
    api_router.include_router(register_router, tags=["register"], prefix="/register")
    api_router.include_router(reviews_router, tags=["reviews"], prefix="/reviews")
    api_router.include_router(sellers_router, prefix="/sellers")
    api_router.include_router(suppliers_router, tags=["suppliers"], prefix="/suppliers")
    api_router.include_router(users_router, tags=["users"], prefix="/users")

    return api_router


router = create_api_router()
