from __future__ import annotations

from fastapi import FastAPI
from fastapi.requests import Request
from fastapi.responses import JSONResponse
from logger import logger
from starlette import status

from exc import CRUDError


def setup_crud_error_handler(app: FastAPI) -> None:
    @app.exception_handler(CRUDError)
    def crud_error_handler(request: Request, exception: CRUDError) -> JSONResponse:  # noqa
        logger.debug(
            "Error: status code(%s): %s: %s"
            % (status.HTTP_400_BAD_REQUEST, type(exception), str(exception))
        )

        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={
                "ok": False,
                "error": str(exception),
                "error_code": status.HTTP_400_BAD_REQUEST,
            },
        )
