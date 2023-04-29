from sqlalchemy.orm import Mapped, mapped_column

from .core import ORMModel, str_20


class NumberEmployeesModel(ORMModel):
    number: Mapped[str_20] = mapped_column(unique=True)
