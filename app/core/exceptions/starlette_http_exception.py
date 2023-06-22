from __future__ import annotations

from fastapi import FastAPI
from fastapi.requests import Request
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from logger import logger


def setup_starlette_http_exception_handler(app: FastAPI) -> None:
    @app.exception_handler(StarletteHTTPException)
    def starlette_http_exception_handler(
        request: Request, exception: StarletteHTTPException  # noqa
    ) -> JSONResponse:
        logger.debug(
            "Error: status code(%s): %s: %s"
            % (exception.status_code, type(exception), exception.detail)
        )

        return JSONResponse(
            status_code=exception.status_code,
            content={
                "ok": False,
                "error": exception.detail,
                "error_code": exception.status_code,
            },
            headers=exception.headers,
        )
