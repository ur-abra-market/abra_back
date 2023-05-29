from fastapi import FastAPI

from .application_error import setup_application_error_handler
from .auth_jwt import setup_auth_jwt_exception_handler
from .exception import setup_exception_handler
from .http_exception import setup_http_exception_handler
from .integrity_error import setup_integrity_error_handler
from .request_validation_error import setup_request_validation_error_handler
from .starlette_http_exception import setup_starlette_http_exception_handler
from .unique_violation_error import setup_unique_violation_error_handler
from .validation_error import setup_validation_error_handler

__all__ = ("setup",)


def setup(app: FastAPI) -> None:
    setup_application_error_handler(app=app)
    setup_auth_jwt_exception_handler(app=app)
    setup_exception_handler(app=app)
    setup_http_exception_handler(app=app)
    setup_integrity_error_handler(app=app)
    setup_request_validation_error_handler(app=app)
    setup_starlette_http_exception_handler(app=app)
    setup_unique_violation_error_handler(app=app)
    setup_validation_error_handler(app=app)
