from fastapi import FastAPI

from .cors import setup_cors_middleware
from .logging import set_request_logging_middleware, init_custom_logging
from core.settings import logging_settings

__all__ = ("setup",)


def setup(app: FastAPI) -> None:
    setup_cors_middleware(app=app)
    if logging_settings.CUSTOM_LOGGING_ON:
        init_custom_logging()
        set_request_logging_middleware(app=app)
