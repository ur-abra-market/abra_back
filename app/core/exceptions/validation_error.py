from __future__ import annotations

from fastapi import FastAPI
from fastapi.requests import Request
from fastapi.responses import JSONResponse
from loguru import logger
from pydantic import ValidationError
from starlette import status


def setup_validation_error_handler(app: FastAPI) -> None:
    @app.exception_handler(ValidationError)
    def validation_error(request: Request, exception: ValidationError) -> JSONResponse:  # noqa
        logger.debug(
            "Error: status code(%s): %s: %s"
            % (status.HTTP_422_UNPROCESSABLE_ENTITY, type(exception), exception.errors())
        )

        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content={
                "ok": False,
                "error": exception.errors(),
                "error_code": status.HTTP_422_UNPROCESSABLE_ENTITY,
            },
        )
