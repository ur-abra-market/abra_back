from __future__ import annotations

from typing import TYPE_CHECKING, Optional

from sqlalchemy.orm import Mapped, relationship

from app.orm.core import ORMModel, mixins, str_100

if TYPE_CHECKING:
    from app.orm.supplier import SupplierModel


class CompanyModel(mixins.BusinessEmailMixin, mixins.PhoneMixin, mixins.SupplierIDMixin, ORMModel):
    name: Mapped[str_100]

    is_manufacturer: Mapped[Optional[bool]]
    year_established: Mapped[Optional[int]]
    number_of_employees: Mapped[Optional[int]]
    description: Mapped[Optional[str]]
    address: Mapped[Optional[str]]
    logo_url: Mapped[Optional[str]]
    business_sector: Mapped[Optional[str_100]]
    photo_url: Mapped[Optional[str]]

    supplier: Mapped[Optional[SupplierModel]] = relationship(
        back_populates="company"
    )
