from __future__ import annotations

from typing import Generic, Type, TypeVar

from .operations import Delete, Get, Insert, Update

ClassT = TypeVar("ClassT")


class ORMAccessor(
    Delete[ClassT],
    Get[ClassT],
    Insert[ClassT],
    Update[ClassT],
    Generic[ClassT],
):
    def __init__(self, model: Type[ClassT]) -> None:
        self.model = model
