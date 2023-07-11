from __future__ import annotations

from typing import TYPE_CHECKING, Any, Tuple, cast

import stringcase
from sqlalchemy.orm import DeclarativeBase, declared_attr

from . import mixins


class ORMModel(mixins.IDMixin, DeclarativeBase):
    if TYPE_CHECKING:
        __table_args__: Tuple[Any, ...]

    @declared_attr  # type: ignore
    def __tablename__(cls) -> str:  # noqa
        return cast(str, stringcase.snakecase(cls.__name__.split("Model")[0]))
