from .addresses import router as addresses_router
from .avatar import router as avatar_router
from .base import router
from .cart import router as cart_router
from .favorites import router as favorites_router
from .notifications import router as notifications_router
from .orders import router as orders_router

emoji = "🛒"

router.include_router(
    addresses_router, tags=[f"{emoji} [sellers] - addresses"], prefix="/addresses"
)
router.include_router(avatar_router, tags=[f"{emoji} [sellers] - avatar"], prefix="/avatar")
router.include_router(cart_router, tags=[f"{emoji} [sellers] - cart"], prefix="/cart")
router.include_router(
    favorites_router, tags=[f"{emoji} [sellers] - favorites"], prefix="/favorites"
)
router.include_router(
    notifications_router, tags=[f"{emoji} [sellers] - notifications"], prefix="/notifications"
)
router.include_router(orders_router, tags=[f"{emoji} [sellers] - orders"], prefix="/orders")
