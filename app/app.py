# mypy: disable-error-code="return-value"

from __future__ import annotations

from fastapi import FastAPI
from fastapi_jwt_auth import AuthJWT
from loguru import logger
from starlette import status

from api import api_router
from core.exceptions import setup as setup_exception_handlers
from core.logger import setup_logger
from core.middleware import setup as setup_middleware
from core.security import Settings
from core.settings import fastapi_settings, swagger_settings
from schemas import ApplicationResponse


def create_application() -> FastAPI:
    """
    Setup FastAPI application: middleware, exception handlers, jwt, logger.
    """

    application = FastAPI(
        title="wb_platform",
        description="API for wb_platform.",
        version="0.0.1",
        debug=fastapi_settings.DEBUG,
        docs_url=swagger_settings.DOCS_URL,
        redoc_url=swagger_settings.REDOC_URL,
        openapi_url=swagger_settings.OPENAPI_URL,
    )
    application.include_router(api_router)

    setup_middleware(application)
    setup_exception_handlers(application)
    setup_logger()

    def get_config() -> Settings:
        return Settings()

    AuthJWT.load_config(get_config)

    @application.on_event("startup")
    async def startup() -> None:
        logger.info("Application startup")

    @application.on_event("shutdown")
    async def shutdown() -> None:
        logger.warning("Application shutdown")

    @application.get(
        path="/",
        response_model=ApplicationResponse[bool],
        status_code=status.HTTP_200_OK,
    )
    async def healthcheck() -> ApplicationResponse[bool]:
        return {
            "ok": True,
            "result": True,
        }

    return application


app = create_application()
