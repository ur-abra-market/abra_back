from fastapi import FastAPI

from .auth_jwt import setup_auth_jwt_exception_handler
from .http_exception import setup_http_exception_handler

__all__ = ("setup",)


def setup(app: FastAPI) -> None:
    setup_auth_jwt_exception_handler(app=app)
    setup_http_exception_handler(app=app)
