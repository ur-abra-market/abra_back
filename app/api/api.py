from fastapi import APIRouter

from .routers import (
    categories_router,
    login_router,
    logout_router,
    password_router,
    register_router,
    reviews_router,
)


def create_api_router() -> APIRouter:
    api_router = APIRouter()
    api_router.include_router(categories_router, tags=["categories"], prefix="/categories")
    api_router.include_router(login_router, tags=["login"], prefix="/login")
    api_router.include_router(logout_router, tags=["logout"], prefix="/logout")
    api_router.include_router(password_router, tags=["password"], prefix="/password")
    api_router.include_router(register_router, tags=["register"], prefix="/register")
    api_router.include_router(reviews_router, tags=["reviews"], prefix="/reviews")

    return api_router


router = create_api_router()
