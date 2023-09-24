from .account import router as account_router
from .base import router
from .business_info import router as business_info_router
from .company import router as company_router
from .notifications import router as notification_router
from .orders import router as order_router
from .products import router as product_router

router.include_router(account_router, tags=["◉ [suppliers] - account"], prefix="")
router.include_router(business_info_router, tags=["[suppliers] - business info"], prefix="/businessInfo")
router.include_router(notification_router, tags=["[suppliers] - notifications"], prefix="/notifications")
router.include_router(company_router, tags=["[suppliers] - company"], prefix="/company")
router.include_router(order_router, tags=["[suppliers] - orders"], prefix="/orders")
router.include_router(product_router, tags=["[suppliers] - products"], prefix="/products")
