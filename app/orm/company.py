from __future__ import annotations

from typing import TYPE_CHECKING, List

from sqlalchemy.orm import Mapped, relationship

from .core import ORMModel, bool_false, mixins, str_30, str_100, text

if TYPE_CHECKING:
    from .company_image import CompanyImageModel
    from .supplier import SupplierModel


class CompanyModel(mixins.BusinessEmailMixin, mixins.PhoneMixin, mixins.SupplierIDMixin, ORMModel):
    name: Mapped[str_100]

    is_manufacturer: Mapped[bool_false]
    year_established: Mapped[int]
    number_of_employees: Mapped[int]
    description: Mapped[text]
    address: Mapped[text]
    logo_url: Mapped[text]
    business_sector: Mapped[str_30]

    images: Mapped[List[CompanyImageModel]] = relationship(back_populates="company")
    supplier: Mapped[SupplierModel] = relationship(back_populates="company")
