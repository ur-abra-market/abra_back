from fastapi import FastAPI
from fastapi.requests import Request
from fastapi.responses import JSONResponse
from fastapi_jwt_auth.exceptions import AuthJWTException


def setup_exception_handlers(app: FastAPI) -> None:
    setup_auth_jwt_exception_handler(app=app)


def setup_auth_jwt_exception_handler(app: FastAPI) -> None:
    @app.exception_handler(AuthJWTException)
    def authjwt_exception_handler(request: Request, exc: AuthJWTException):
        return JSONResponse(status_code=exc.status_code, content={"detail": exc.message})
