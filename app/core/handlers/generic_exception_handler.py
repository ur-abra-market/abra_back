from fastapi import FastAPI
from fastapi.requests import Request
from starlette.responses import JSONResponse

from core.exceptions import ApplicationException
from logger import logger
from schemas import SimpleAPIError


def setup_generic_exception_handler(app: FastAPI) -> None:
    @app.exception_handler(ApplicationException)
    def generic_exception_handler(
        request: Request, exception: ApplicationException
    ) -> JSONResponse:
        logger.debug(
            "Error: status code(%s): %s: %s"
            % (exception.status_code, type(exception), exception.detail)
        )

        return JSONResponse(
            status_code=exception.status_code,
            headers=exception.headers,
            content=SimpleAPIError(detail=exception.detail).dict(),
        )
