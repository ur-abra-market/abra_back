from fastapi import FastAPI

from logger import logger

from .cors import setup_cors_middleware
from .logging import setup_logging_middleware

__all__ = ("setup",)


def setup(app: FastAPI) -> None:
    setup_cors_middleware(app=app)
    setup_logging_middleware(app=app)

    logger.info(
        "Mounted middleware: %s"
        % (" ".join([middleware.cls.__name__ for middleware in app.user_middleware]))
    )
