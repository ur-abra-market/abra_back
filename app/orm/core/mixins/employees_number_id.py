from __future__ import annotations

from sqlalchemy.orm import Mapped

from ..constraints import employees_number_id_fk
from ..types import employees_number_id_fk_type


class EmployeesNumberIDMixin:
    employees_number_id: Mapped[employees_number_id_fk_type] = employees_number_id_fk
