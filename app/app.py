from __future__ import annotations

from fastapi import FastAPI
from fastapi_jwt_auth import AuthJWT
from starlette import status

from admin import create_sqlalchemy_admin
from api import api_router
from core.depends.google_token import google_verifier
from core.exceptions import setup as setup_exception_handlers
from core.middleware import setup as setup_middleware
from core.security import Settings
from core.settings import application_settings, fastapi_uvicorn_settings
from logger import logger
from schemas import ApplicationResponse
from typing_ import RouteReturnT


def create_application() -> FastAPI:
    """
    Setup FastAPI application: middleware, exception handlers, jwt, logger.
    """

    application = FastAPI(
        title="Abra",
        description=f"<b>API for Abra:</b> {application_settings.ENV}<br>({application_settings.COMMIT})",
        version="0.0.1",
        debug=fastapi_uvicorn_settings.DEBUG,
        docs_url=fastapi_uvicorn_settings.DOCS_URL,
        redoc_url=fastapi_uvicorn_settings.REDOC_URL,
        openapi_url=fastapi_uvicorn_settings.OPENAPI_URL,
    )
    application.include_router(api_router)

    setup_middleware(application)
    setup_exception_handlers(application)

    def create_auth() -> None:
        def get_config() -> Settings:
            return Settings()

        AuthJWT.load_config(get_config)

    def create_on_event() -> None:
        @application.on_event("startup")
        async def startup() -> None:
            logger.info("Application startup")

        @application.on_event("shutdown")
        async def shutdown() -> None:
            logger.warning("Application shutdown")

        @application.on_event("shutdown")
        async def google_verifier_shutdown() -> None:
            await google_verifier.close()

    def create_routes() -> None:
        @application.get(
            path="/",
            response_model=ApplicationResponse[bool],
            status_code=status.HTTP_200_OK,
        )
        async def healthcheck() -> RouteReturnT:
            logger.info("Healthcheck called")

            return {
                "ok": True,
                "result": True,
            }

    def create_admin_panel() -> None:
        logger.info("Creating an admin panel is only available in debug mode, status: ...")
        if fastapi_uvicorn_settings.DEBUG:
            sqlalchemy_admin = create_sqlalchemy_admin()
            sqlalchemy_admin.mount_to(application)

            logger.info("Admin panel was successfully created!")
        else:
            logger.info("Admin panel is not available")

    create_auth()
    create_on_event()
    create_routes()
    create_admin_panel()

    return application


app = create_application()
