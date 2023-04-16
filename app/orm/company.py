from __future__ import annotations

from typing import TYPE_CHECKING, List, Optional

from sqlalchemy.orm import Mapped, relationship

from .core import ORMModel, bool_false, mixins, str_30, str_100, text

if TYPE_CHECKING:
    from .company_image import CompanyImageModel
    from .supplier import SupplierModel


class CompanyModel(mixins.BusinessEmailMixin, mixins.PhoneMixin, mixins.SupplierIDMixin, ORMModel):
    name: Mapped[Optional[str_100]]

    is_manufacturer: Mapped[bool_false]
    year_established: Mapped[Optional[int]]
    number_of_employees: Mapped[Optional[int]]
    description: Mapped[Optional[text]]
    address: Mapped[Optional[text]]
    logo_url: Mapped[Optional[text]]
    business_sector: Mapped[Optional[str_30]]

    images: Mapped[List[CompanyImageModel]] = relationship(back_populates="company")
    supplier: Mapped[Optional[SupplierModel]] = relationship(back_populates="company")
