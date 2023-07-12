from __future__ import annotations

from typing import TYPE_CHECKING, List, Optional

from sqlalchemy import CheckConstraint
from sqlalchemy.orm import Mapped, relationship

from .core import ORMModel, mixins, types

if TYPE_CHECKING:
    from company_phone import CompanyPhoneModel

    from .company_image import CompanyImageModel
    from .country import CountryModel
    from .supplier import SupplierModel


class CompanyModel(
    mixins.BusinessEmailMixin,
    mixins.SupplierIDMixin,
    mixins.CountryIDMixin,
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
    number_employees: Mapped[types.small_int]
    description: Mapped[Optional[types.text]]
    address: Mapped[Optional[types.text]]
    logo_url: Mapped[Optional[types.text]]
    business_sector: Mapped[types.str_50]

    country: Mapped[Optional[CountryModel]] = relationship(back_populates="companies")
    phone: Mapped[Optional[CompanyPhoneModel]] = relationship(back_populates="company")
    images: Mapped[List[CompanyImageModel]] = relationship(back_populates="company")
    supplier: Mapped[Optional[SupplierModel]] = relationship(back_populates="company")
