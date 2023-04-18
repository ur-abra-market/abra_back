from __future__ import annotations

from fastapi import FastAPI
from fastapi.requests import Request
from fastapi.responses import JSONResponse
from loguru import logger
from starlette import status

from exc import ColumnNotFound


def setup_column_not_found_handler(app: FastAPI) -> None:
    @app.exception_handler(ColumnNotFound)
    def column_not_found_handler(
        request: Request, exception: ColumnNotFound
    ) -> JSONResponse:  # noqa
        logger.debug(
            "Error: status code(%s): %s: %s"
            % (status.HTTP_500_INTERNAL_SERVER_ERROR, type(exception), str(exception))
        )

        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "ok": False,
                "error": "Internal service errors are not displayed in here",
                "error_code": status.HTTP_500_INTERNAL_SERVER_ERROR,
            },
        )
