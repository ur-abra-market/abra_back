from __future__ import annotations

from asyncpg import UniqueViolationError
from fastapi import FastAPI
from fastapi.requests import Request
from fastapi.responses import JSONResponse
from starlette import status

from logger import logger


def setup_unique_violation_error_handler(app: FastAPI) -> None:
    @app.exception_handler(UniqueViolationError)
    def unique_violation_error_handler(
        request: Request, exception: UniqueViolationError  # noqa
    ) -> JSONResponse:
        logger.debug(
            "Error: status code(%s): %s: %s"
            % (status.HTTP_409_CONFLICT, type(exception), str(exception))
        )

        return JSONResponse(
            status_code=status.HTTP_409_CONFLICT,
            content={
                "ok": False,
                "error": "The field already exists, try using a different value, possibly another email address",
                "error_code": status.HTTP_409_CONFLICT,
            },
        )
