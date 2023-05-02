from __future__ import annotations

import asyncio
import uuid
from typing import Any, Awaitable, Callable, Optional, Type

from fastapi import FastAPI
from fastapi.requests import Request
from fastapi.responses import JSONResponse
from pydantic import UUID4, BaseModel
from starlette.middleware.base import BaseHTTPMiddleware

from logger import logger
from typing_ import DictStrAny

from ._responses import ERROR_RESPONSE


class _ExceptionInfo(BaseModel):
    type: Type[BaseException]
    exception: Optional[str]


class _RequestInfo(BaseModel):
    method: str
    url: str


class _ResponseInfo(BaseModel):
    duration: float
    status_code: int


class _RequestMetadata(BaseModel):
    request_id: UUID4
    request_info: _RequestInfo
    response_info: _ResponseInfo
    exception_info: Optional[_ExceptionInfo] = None


def _request_metadata(
    request: Request,
    response: JSONResponse,
    duration: float,
    exception: Optional[Any] = None,
) -> _RequestMetadata:
    return _RequestMetadata(
        request_id=uuid.uuid4(),
        request_info=_RequestInfo(
            method=request.method,
            url=request.url._url,  # noqa
        ),
        response_info=_ResponseInfo(
            duration=duration,
            status_code=response.status_code,
        ),
        exception_info=_ExceptionInfo(
            type=type(exception),
            exception=str(exception),
        )
        if exception
        else None,
    )


async def logging_middleware(
    request: Request, call_next: Callable[[Request], Awaitable[JSONResponse]]
) -> JSONResponse:
    _kwargs: DictStrAny = {"request": request}

    loop = asyncio.get_event_loop()
    start_time = loop.time()

    try:
        response = await call_next(request)
    except Exception as exception:
        response = ERROR_RESPONSE

        _kwargs.update(exception=exception)

    _kwargs.update({"response": response, "duration": round(loop.time() - start_time, 5)})
    logger.info("Request processing", extra=_request_metadata(**_kwargs).dict())

    return response


def setup_logging_middleware(app: FastAPI) -> None:
    app.add_middleware(BaseHTTPMiddleware, dispatch=logging_middleware)
