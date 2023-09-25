from .account import router as account_router
from .base import router
from .password import router as password_router
from .searches import router as searches_router


emoji = "👤"

router.include_router(account_router, tags=[f'{emoji} [users] - account'], prefix='/account')
router.include_router(password_router, tags=[f'{emoji} [users] - password'], prefix='/password')
router.include_router(searches_router, tags=[f'{emoji} [users] - searches'], prefix='/searches')
