from __future__ import annotations

from fastapi import FastAPI
from fastapi.requests import Request
from fastapi.responses import JSONResponse
from loguru import logger
from starlette import status

from exc import ResultRequired


def setup_result_required_handler(app: FastAPI) -> None:
    @app.exception_handler(ResultRequired)
    def result_required_handler(
        request: Request, exception: ResultRequired  # noqa
    ) -> JSONResponse:
        logger.debug(
            "Error: status code(%s): %s: %s"
            % (status.HTTP_404_NOT_FOUND, type(exception), str(exception))
        )

        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={
                "ok": False,
                "error": "Not found",
                "error_code": status.HTTP_404_NOT_FOUND,
            },
        )
