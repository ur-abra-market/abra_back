from fastapi import FastAPI
from fastapi_jwt_auth import AuthJWT
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

    @AuthJWT.load_config
    def get_config() -> Settings:
        return Settings()

    @application.on_event("startup")
    async def startup() -> None:
        from orm.core import ORMModel
        from orm.core.session import _engine

        # async with _engine.begin() as connection:
        # await connection.run_sync(ORMModel.metadata.drop_all)
        # await connection.run_sync(ORMModel.metadata.create_all)

    @application.on_event("shutdown")
    async def shutdown() -> None:
        ...

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
