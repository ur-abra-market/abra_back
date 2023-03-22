import time
import traceback
import uuid

from fastapi import FastAPI, Request, Response
from loguru import logger
from starlette.middleware.base import BaseHTTPMiddleware


class LogginMiddleware(BaseHTTPMiddleware):
    """Middleware for adding additional info to logs."""

    async def dispatch(self, request: Request, call_next) -> Response:
        error = None
        request_metadata = {"request_id": str(uuid.uuid4())}
        request_metadata["method"] = request.method
        request_metadata["url"] = request.url.path

        # TODO: we can add additional fields such as ip, country, headers etc.

        start_time = time.perf_counter()
        try:
            response = await call_next(request)
            user_profile = request.state.__dict__["_state"].get("user_profile", None)
            if user_profile:
                user_profile = user_profile.id
            request_metadata["profile_id"] = user_profile or "unknown user"
            request_metadata["status_code"] = response.status_code

        except Exception as _e:
            full_traceback = traceback.format_tb(_e.__traceback__, 30)
            exc_info = traceback.extract_tb(_e.__traceback__)[-1]

            request_metadata["exception_info"] = {
                "type": str(_e),
                "filename": exc_info.filename,
                "line": exc_info.line,
                "func": exc_info.name,
                "full_traceback": full_traceback,
            }
            request_metadata["status_code"] = 500
            error = _e

        finally:
            duration = time.perf_counter() - start_time
            request_metadata["duration"] = round(duration, 5)

        if error:
            logger.error("", err=str(error), **request_metadata)
            return Response(status_code=500)

        if not error:
            logger.info("", **request_metadata)
            return response


def set_up_logging_middleware(app: FastAPI) -> None:
    app.add_middleware(LogginMiddleware)
