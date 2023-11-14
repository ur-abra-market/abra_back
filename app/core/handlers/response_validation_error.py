from __future__ import annotations

from fastapi import FastAPI
from fastapi.requests import Request
from fastapi.responses import JSONResponse
from pydantic import ValidationError
from starlette import status

from logger import logger
from schemas import SimpleAPIError


def setup_response_validation_error_handler(app: FastAPI) -> None:
    @app.exception_handler(ValidationError)
    def response_validation_error(
        request: Request, exception: ValidationError
    ) -> JSONResponse:  # noqa
        logger.debug(
            "Error: status code(%s): %s: %s"
            % (status.HTTP_422_UNPROCESSABLE_ENTITY, type(exception), exception.errors())
        )

        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content=SimpleAPIError(detail=exception.errors()).dict(),
        )
