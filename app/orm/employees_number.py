from __future__ import annotations

from typing import TYPE_CHECKING, Optional

from sqlalchemy.orm import Mapped, mapped_column, relationship

from .core import ORMModel, types

if TYPE_CHECKING:
    from .company import CompanyModel


class EmployeesNumberModel(ORMModel):
    number: Mapped[types.str_20] = mapped_column(unique=True)

    company: Mapped[Optional[CompanyModel]] = relationship(back_populates="employees_number")
