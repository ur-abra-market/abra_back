from .account import router as account_router
from .base import router
from .business_info import router as business_info_router
from .company import router as company_router
from .notifications import router as notification_router
from .orders import router as order_router
from .products import router as product_router

emoji = "💼"

router.include_router(account_router, tags=[f"{emoji} [suppliers] - account"], prefix="")
router.include_router(
    business_info_router, tags=[f"{emoji} [suppliers] - business info"], prefix="/businessInfo"
)
router.include_router(
    notification_router, tags=[f"{emoji} [suppliers] - notifications"], prefix="/notifications"
)
router.include_router(company_router, tags=[f"{emoji} [suppliers] - company"], prefix="/company")
router.include_router(order_router, tags=[f"{emoji} [suppliers] - orders"], prefix="/orders")
router.include_router(product_router, tags=[f"{emoji} [suppliers] - products"], prefix="/products")
