from fastapi import FastAPI

from .attribute_error import setup_attribute_error_exception_handler
from .auth_jwt import setup_auth_jwt_exception_handler
from .generic_exception_handler import setup_generic_exception_handler
from .postgres_error import setup_postgres_error_handler
from .request_validation_error import setup_request_validation_error_handler
from .response_validation_error import setup_response_validation_error_handler
from .sqlalchemy_error import setup_sqlalchemy_error_handler

__all__ = ("setup",)


def setup(app: FastAPI) -> None:
    setup_auth_jwt_exception_handler(app=app)
    setup_attribute_error_exception_handler(app=app)
    setup_generic_exception_handler(app=app)
    setup_postgres_error_handler(app=app)
    setup_response_validation_error_handler(app=app)
    setup_request_validation_error_handler(app=app)
    setup_sqlalchemy_error_handler(app=app)
