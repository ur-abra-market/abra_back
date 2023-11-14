from __future__ import annotations

import asyncio
import uuid
from typing import Awaitable, Callable

from fastapi import FastAPI
from fastapi.requests import Request
from fastapi.responses import JSONResponse, Response
from starlette import status
from starlette.middleware.base import BaseHTTPMiddleware

from logger import logger
from schemas import SimpleAPIError


async def logging_middleware(
    request: Request, call_next: Callable[[Request], Awaitable[Response]]
) -> Response:
    loop = asyncio.get_event_loop()
    start_time = loop.time()

    try:
        response = await call_next(request)
    except Exception as exception:
        logger.exception(exception)

        response = JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content=SimpleAPIError(detail="Unhandled error").dict(),
        )

    logger.info(
        "Middleware - ID [%s] -  TIME [%ss] - CLIENT [%s][%s][%s] - RESPONSE [%s]"
        % (
            uuid.uuid4(),
            round(loop.time() - start_time, 5),
            request.method,
            request.url,
            request.client,
            response.status_code,
        )
    )

    return response


def setup_logging_middleware(app: FastAPI) -> None:
    app.add_middleware(BaseHTTPMiddleware, dispatch=logging_middleware)
