from fastapi import FastAPI
from fastapi.requests import Request
from fastapi.responses import JSONResponse
from fastapi_jwt_auth.exceptions import AuthJWTException


def setup_auth_jwt_exception_handler(app: FastAPI) -> None:
    @app.exception_handler(AuthJWTException)
    def authjwt_exception_handler(request: Request, exception: AuthJWTException) -> JSONResponse:
        return JSONResponse(
            status_code=exception.status_code,
            content={
                "ok": False,
                "error": exception.message,
            },
        )
