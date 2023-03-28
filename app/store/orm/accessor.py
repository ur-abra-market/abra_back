from __future__ import annotations

from typing import Generic, TypeVar

from orm.core import ORMModel

from .operations import Delete, Get, Insert, Update

ClassT = TypeVar("ClassT", bound=ORMModel)


class ORMAccessor(
    Delete[ClassT],
    Get[ClassT],
    Insert[ClassT],
    Update[ClassT],
    Generic[ClassT],
):
    def __init__(self, model: ClassT) -> None:
        self.model = model
