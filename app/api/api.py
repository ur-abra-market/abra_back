from fastapi import APIRouter

from .routers import categories_router, password_router, register_router, test_router


def create_api_router() -> APIRouter:
    api_router = APIRouter()
    api_router.include_router(categories_router)
    api_router.include_router(password_router)
    api_router.include_router(register_router)
    api_router.include_router(test_router)

    return api_router


router = create_api_router()
