from typing import Any

from fastapi import FastAPI
from fastapi_jwt_auth import AuthJWT
from starlette import status

from app.api import api_router
from app.classes.response_models import Settings
from app.core.exceptions import setup_exception_handlers
from app.core.logger import setup_logger
from app.core.middleware import setup as setup_middleware
from app.core.settings import fastapi_settings, swagger_settings
from app.logic.utils import Dict


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

    return application


app = create_application()


@app.get(
    path="/",
    status_code=status.HTTP_200_OK
)
async def root() -> Dict[str, Any]:
    return {"detail": "ok"}
