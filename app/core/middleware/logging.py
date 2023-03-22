import asyncio
import traceback
import uuid
from typing import Callable, Awaitable

from fastapi import FastAPI
from fastapi.requests import Request
from fastapi.responses import Response, JSONResponse
from loguru import logger
from starlette import status
from starlette.middleware.base import BaseHTTPMiddleware

from core.settings import logging_settings


async def logging_middleware(request: Request, call_next: Callable[[Request], Awaitable[Response]]) -> Response:
    loop = asyncio.get_event_loop()
    request_metadata = {"request_id": str(uuid.uuid4()), "method": request.method, "url": request.url.path}

    response = JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "ok": False,
            "error": "Got error while handling request"
        }
    )

    start_time = loop.time()
    try:
        response = await call_next(request)
    except Exception as e:
        exception_traceback = traceback.format_exc()
        exception_info = traceback.extract_tb(exception_traceback)[-1]

        request_metadata["exception_info"] = {
            "type": type(e),
            "filename": exception_info.filename,
            "line": exception_info.line,
            "func": exception_info.name,
            "exception_traceback": exception_traceback,
        }
        request_metadata["error"] = str(e)
        logger.error(**request_metadata)
        return response
    finally:
        duration = loop.time() - start_time
        request_metadata["duration"] = round(duration, 5)
        request_metadata["status_code"] = response.status_code

    logger.info(**request_metadata)

    return response


def setup_request_logging_middleware(app: FastAPI) -> None:
    if logging_settings.CUSTOM_LOGGING_ON:
        _setup_request_logging_middleware(app=app)


def _setup_request_logging_middleware(app: FastAPI) -> None:
    app.add_middleware(
        BaseHTTPMiddleware,
        dispatch=logging_middleware,
    )