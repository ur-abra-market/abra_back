from __future__ import annotations

from fastapi import FastAPI
from fastapi.requests import Request
from fastapi.responses import JSONResponse
from fastapi_jwt_auth.exceptions import AuthJWTException

from logger import logger
from schemas import SimpleAPIError


def setup_auth_jwt_exception_handler(app: FastAPI) -> None:
    @app.exception_handler(AuthJWTException)
    def authjwt_exception_handler(
        request: Request, exception: AuthJWTException  # noqa
    ) -> JSONResponse:
        logger.debug(
            "Error: status code(%s): %s: %s"
            % (exception.status_code, type(exception), exception.message)
        )

        return JSONResponse(
            status_code=exception.status_code,
            content=SimpleAPIError(detail=exception.message).dict(),
        )
