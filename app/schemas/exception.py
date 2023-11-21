from typing import Any, Union

from .schema import ApplicationSchema


class SimpleAPIError(ApplicationSchema):
    """A simple model for HTTP errors."""

    detail: Union[str, list[Any]]
