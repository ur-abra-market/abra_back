from __future__ import annotations

from fastapi import FastAPI
from fastapi.requests import Request
from fastapi.responses import JSONResponse
from sqlalchemy.exc import IntegrityError
from starlette import status

from logger import logger


def setup_integrity_error_handler(app: FastAPI) -> None:
    @app.exception_handler(IntegrityError)
    def integrity_error_handler(
        request: Request, exception: IntegrityError
    ) -> JSONResponse:  # noqa
        logger.debug("Error: status code(%s)" % status.HTTP_409_CONFLICT)
        logger.exception(exception)

        return JSONResponse(
            status_code=status.HTTP_409_CONFLICT,
            content={
                "ok": False,
                "error": "Possible errors: " "email exists, " "id exists. " "Try another data!",
                "error_code": status.HTTP_409_CONFLICT,
            },
        )
