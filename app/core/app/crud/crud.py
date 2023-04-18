from __future__ import annotations

from typing import Generic, Type, TypeVar

from .operations import Delete, Get, GetBy, Insert, Update

ClassT = TypeVar("ClassT")


class CRUD(
    Delete[ClassT],
    GetBy[ClassT],
    Get[ClassT],
    Insert[ClassT],
    Update[ClassT],
    Generic[ClassT],
):
    def __init__(self, model: Type[ClassT]) -> None:
        self.__model__ = model
