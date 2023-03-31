from fastapi import FastAPI
from fastapi.exceptions import HTTPException
from fastapi.requests import Request
from fastapi.responses import JSONResponse


def setup_http_exception_handler(app: FastAPI) -> None:
    @app.exception_handler(HTTPException)
    def http_exception_handler(
        request: Request, exception: HTTPException
    ) -> JSONResponse:
        return JSONResponse(
            status_code=exception.status_code,
            content={
                "ok": False,
                "error": exception.detail,
            },
            headers=exception.headers,
        )
