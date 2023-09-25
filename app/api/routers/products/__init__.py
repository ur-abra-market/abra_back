from .base import router
from .info import router as info_router
from .reviews import router as reviews_router
from .selection import router as selection_router


emoji = "👚"

router.include_router(info_router, tags=[f'{emoji} [products] - info'], prefix='/{product_id}')
router.include_router(reviews_router, tags=[f'{emoji} [products] - reviews'], prefix='/{product_id}/reviews')
router.include_router(selection_router, tags=[f'{emoji} [products] - selection'], prefix='')
