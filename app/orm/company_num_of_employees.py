from sqlalchemy.orm import Mapped, mapped_column

from .core import ORMModel, str_20


class CompanyNumOfEmployeeModel(ORMModel):
    num_of_employees: Mapped[str_20] = mapped_column(
        unique=True,
    )
