from .base import router
from .info import router as info_router

emoji = "📄"

router.include_router(info_router, tags=[f"{emoji} [common] - info"], prefix="")
