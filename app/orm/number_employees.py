from __future__ import annotations

from sqlalchemy.orm import Mapped, mapped_column

from .core import ORMModel, types


class NumberEmployeesModel(ORMModel):
    number: Mapped[types.str_20] = mapped_column(unique=True)
