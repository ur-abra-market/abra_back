from .base import router
from .info import router as info_router
from .sign_in import router as signin_router
from .sign_out import router as signout_router
from .sign_up import router as signup_router

emoji = "🔐"

router.include_router(info_router, tags=[f"{emoji} [auth] - info"], prefix="/sign-in")
router.include_router(signin_router, tags=[f"{emoji} [auth] - sign-in (login)"], prefix="/sign-in")
router.include_router(
    signout_router, tags=[f"{emoji} [auth] - sign-out (logout)"], prefix="/sign-out"
)
router.include_router(
    signup_router, tags=[f"{emoji} [auth] - sign-up (register)"], prefix="/sign-up"
)
