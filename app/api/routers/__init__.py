from fastapi import APIRouter

from .categories import categories as categories_router
from .login import login as login_router
from .logout import logout as logout_router
from .password import password as password_router
from .products import products as products_router
from .register import register as register_router
from .reviews import reviews as reviews_router
from .sellers import sellers as sellers_router
from .suppliers import suppliers as suppliers_router
from .users import users as users_router

router = APIRouter()
router.include_router(categories_router, tags=["categories"], prefix="/categories")
router.include_router(login_router, tags=["login"], prefix="/login")
router.include_router(logout_router, tags=["logout"], prefix="/logout")
router.include_router(password_router, tags=["password"], prefix="/password")
router.include_router(products_router, tags=["products"], prefix="/products")
router.include_router(register_router, tags=["register"], prefix="/register")
router.include_router(reviews_router, tags=["reviews"], prefix="/reviews")
router.include_router(suppliers_router, tags=["suppliers"], prefix="/suppliers")
router.include_router(sellers_router, tags=["sellers"], prefix="/sellers")
router.include_router(users_router, tags=["users"], prefix="/users")

__all__ = ("router",)
