from fastapi import FastAPI

from .cors import setup_cors_middleware
from .logging import setup_logging_middleware

__all__ = ("setup",)


def setup(app: FastAPI) -> None:
    setup_cors_middleware(app=app)
