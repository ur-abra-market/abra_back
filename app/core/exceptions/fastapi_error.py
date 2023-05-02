from __future__ import annotations

from fastapi import FastAPI
from fastapi.exceptions import FastAPIError
from fastapi.requests import Request
from fastapi.responses import JSONResponse
from starlette import status

from logger import logger


def setup_fastapi_error_handler(app: FastAPI) -> None:
    @app.exception_handler(FastAPIError)
    def fastapi_error_handler(request: Request, exception: FastAPIError) -> JSONResponse:  # noqa
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
