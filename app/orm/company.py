from __future__ import annotations

from typing import TYPE_CHECKING, List, Optional

from sqlalchemy import CheckConstraint
from sqlalchemy.orm import Mapped, relationship

from .core import ORMModel, bool_false, mixins, str_50, str_100, text

if TYPE_CHECKING:
    from .company_image import CompanyImageModel
    from .supplier import SupplierModel


class CompanyModel(mixins.BusinessEmailMixin, mixins.PhoneMixin, mixins.SupplierIDMixin, ORMModel):
    __table_args__ = (
        CheckConstraint(
            "year_established  > 1800 and year_established <= extract(year FROM CURRENT_DATE)::int",
            name="year_established_between_1800_and_today",
        ),
        CheckConstraint(""),
    )

    name: Mapped[str_100]

    is_manufacturer: Mapped[bool_false]
    year_established: Mapped[int]
    number_of_employees: Mapped[int]
    description: Mapped[text]
    address: Mapped[text]
    logo_url: Mapped[text]
    business_sector: Mapped[str_50]

    images: Mapped[List[CompanyImageModel]] = relationship(back_populates="company")
    supplier: Mapped[Optional[SupplierModel]] = relationship(back_populates="company")
