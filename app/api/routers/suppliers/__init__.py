from .base import router
from .orders import router as order_router
from .products import router as product_router


router.include_router(order_router, tags=['suppliers-orders'], prefix='/orders')
router.include_router(product_router, tags=['suppliers-products'], prefix='/products')
