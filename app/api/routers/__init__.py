from .auth import router as auth_router
from .categories import router as categories_router
from .common import router as common_router
from .password import router as password_router
from .products import router as products_router
from .register import router as register_router
from .reviews import router as reviews_router
from .sellers import router as sellers_router
from .suppliers import router as suppliers_router
from .users import router as users_router

__all__ = (
    "auth_router",
    "categories_router",
    "common_router",
    "password_router",
    "products_router",
    "register_router",
    "reviews_router",
    "sellers_router",
    "suppliers_router",
    "users_router",
)
