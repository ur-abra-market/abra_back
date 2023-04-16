from .categories import router as categories_router
from .login import router as login_router
from .logout import router as logout_router
from .password import router as password_router
from .products import router as products_router
from .register import router as register_router
from .reviews import router as reviews_router
from .sellers import router as sellers_router
from .suppliers import router as suppliers_router
from .users import router as users_router

__all__ = (
    "categories_router",
    "login_router",
    "logout_router",
    "password_router",
    "products_router",
    "register_router",
    "reviews_router",
    "sellers_router",
    "suppliers_router",
    "users_router",
)
