from __future__ import annotations

from typing import TYPE_CHECKING, List, Optional

from sqlalchemy import CheckConstraint
from sqlalchemy.orm import Mapped, relationship

from .core import ORMModel, mixins, types

if TYPE_CHECKING:
    from company_phone import CompanyPhoneModel

    from .category import CategoryModel
    from .company_image import CompanyImageModel
    from .country import CountryModel
    from .employees_number import EmployeesNumberModel
    from .supplier import SupplierModel


class CompanyModel(
    mixins.BusinessEmailMixin,
    mixins.CountryIDMixin,
    mixins.EmployeesNumberIDMixin,
    mixins.SupplierIDMixin,
    ORMModel,
):
    __table_args__ = (
        CheckConstraint(
            "year_established  > 1960 and year_established <= extract(year FROM CURRENT_DATE)::int",
            name="year_established_between_1960_and_today",
        ),
    )

    name: Mapped[types.str_100]

    is_manufacturer: Mapped[types.bool_false]
    year_established: Mapped[types.small_int]
    description: Mapped[Optional[types.text]]
    address: Mapped[Optional[types.text]]
    logo_url: Mapped[Optional[types.text]]

    country: Mapped[Optional[CountryModel]] = relationship(back_populates="companies")
    phone: Mapped[Optional[CompanyPhoneModel]] = relationship(
        back_populates="company", cascade="all, delete"
    )
    images: Mapped[List[CompanyImageModel]] = relationship(
        back_populates="company", cascade="all, delete"
    )
    supplier: Mapped[Optional[SupplierModel]] = relationship(back_populates="company")
    employees_number: Mapped[Optional[EmployeesNumberModel]] = relationship(
        back_populates="company"
    )
    business_sectors: Mapped[List[CategoryModel]] = relationship(
        secondary="company_business_sector_to_category",
        back_populates="companies",
    )
