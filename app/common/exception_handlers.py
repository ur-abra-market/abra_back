import json

from pydantic import ValidationError
from starlette.responses import JSONResponse
from loguru import logger

from app.common import exceptions
from app.common.enums import ErrorCodes
from app.schemas.exceptions import SimpleApiError


_mapping = {
    exceptions.AuthException: SimpleApiError,
    exceptions.SQLError: SimpleApiError,
    exceptions.AlreadyExistError: SimpleApiError,
    exceptions.NotExistError: SimpleApiError,
    exceptions.NotFoundException: SimpleApiError,
    exceptions.BadRequestException: SimpleApiError,
}


async def generic_exception_handler(request, exc):
    exc_type = type(exc)
    schema = _mapping.get(exc_type, None)
    if schema is None:
        if issubclass(exc_type, exceptions.GenericApiException):
            schema = SimpleApiError
            logger.warning(f"A mapping schema for {exc_type} does not exist. Falling back to {SimpleApiError}")
    if schema is None:
        logger.error(f"A mapping schema for {exc_type} does not exist and it can't be mapped to {SimpleApiError}")
        return JSONResponse(
            status_code=500,
            content=SimpleApiError(code=ErrorCodes.api_error, message="Unknown error"),
        )
    return JSONResponse(status_code=exc.status_code, content=schema.from_orm(exc).dict())


async def validation_exception_handler(request, exc: ValidationError):
    return JSONResponse(status_code=422, content=json.loads(exc.json()))
