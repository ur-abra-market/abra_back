from __future__ import annotations

from asyncpg import PostgresError
from fastapi import FastAPI
from fastapi.requests import Request
from fastapi.responses import JSONResponse
from starlette import status

from logger import logger
from schemas import SimpleAPIError


def setup_postgres_error_handler(app: FastAPI) -> None:
    @app.exception_handler(PostgresError)
    def postgres_error_handler(request: Request, exception: PostgresError) -> JSONResponse:  # noqa
        logger.debug(
            "Error: status code(%s): %s: %s"
            % (status.HTTP_409_CONFLICT, type(exception), exception)
        )

        return JSONResponse(
            status_code=status.HTTP_409_CONFLICT,
            content=SimpleAPIError(detail=f"Database error: {exception}").dict(),
        )
