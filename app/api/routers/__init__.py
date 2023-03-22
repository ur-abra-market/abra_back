from .categories import router as categories_router
from .password import router as password_router
from .register import router as register_router
from .test import router as test_router

__all__ = (
    "categories_router",
    "password_router",
    "register_router",
)
