from __future__ import annotations

import traceback

from fastapi import FastAPI
from fastapi.requests import Request
from fastapi.responses import JSONResponse
from starlette import status

from logger import logger
from schemas import SimpleAPIError


def setup_attribute_error_exception_handler(app: FastAPI) -> None:
    @app.exception_handler(AttributeError)
    def attribute_error_exception_handler(
        request: Request, exception: AttributeError  # noqa
    ) -> JSONResponse:
        logger.debug(
            "Error: status code(%s): %s: %s"
            % (status.HTTP_500_INTERNAL_SERVER_ERROR, type(exception), str(exception))
        )

        traceback.print_exception(None, value=exception, tb=exception.__traceback__)

        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content=SimpleAPIError(detail=f"AttributError. DETAIL: {str(exception)}").dict(),
        )
