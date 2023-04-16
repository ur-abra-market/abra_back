from __future__ import annotations

from typing import cast

import stringcase
from sqlalchemy import types
from sqlalchemy.orm import DeclarativeBase, declared_attr, registry

from . import mixins
from .types import (
    decimal_2_1,
    decimal_3_2,
    decimal_10_2,
    str_4,
    str_14,
    str_15,
    str_16,
    str_20,
    str_25,
    str_30,
    str_36,
    str_50,
    str_100,
    str_200,
)


class ORMModel(mixins.IDMixin, DeclarativeBase):
    registry = registry(
        type_annotation_map={
            int: types.BIGINT(),
            decimal_2_1: types.DECIMAL(2, 1),
            decimal_3_2: types.DECIMAL(3, 2),
            decimal_10_2: types.DECIMAL(10, 2),
            str_4: types.String(4),
            str_14: types.String(14),
            str_15: types.String(15),
            str_16: types.String(16),
            str_20: types.String(20),
            str_25: types.String(25),
            str_30: types.String(30),
            str_36: types.String(36),
            str_50: types.String(50),
            str_100: types.String(100),
            str_200: types.String(200),
        }
    )

    @declared_attr  # type: ignore
    def __tablename__(cls) -> str:  # noqa
        name, _postfix = cls.__name__.split("Model")
        return cast(str, stringcase.snakecase(name))
