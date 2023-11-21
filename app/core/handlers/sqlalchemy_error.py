from __future__ import annotations

import traceback

from fastapi import FastAPI
from fastapi.requests import Request
from fastapi.responses import JSONResponse
from sqlalchemy.exc import SQLAlchemyError
from starlette import status

from logger import logger
from schemas import SimpleAPIError


def setup_sqlalchemy_error_handler(app: FastAPI) -> None:
    @app.exception_handler(SQLAlchemyError)
    def sqlalchemy_error_handler(
        request: Request, exception: SQLAlchemyError  # noqa
    ) -> JSONResponse:
        logger.debug(
            "Error: status code(%s): %s: %s"
            % (status.HTTP_409_CONFLICT, type(exception), exception)
        )
        traceback.print_exception(None, value=exception, tb=exception.__traceback__)

        return JSONResponse(
            status_code=status.HTTP_409_CONFLICT,
            content=SimpleAPIError(detail=f"SQLAlchemy error. DETAIL: {exception}").dict(),
        )
