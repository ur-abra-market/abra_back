from __future__ import annotations

from typing import TYPE_CHECKING, Optional

from sqlalchemy.orm import Mapped, relationship

from .core import ORMModel, mixins, str_100, text

if TYPE_CHECKING:
    from .supplier import SupplierModel


class CompanyModel(
    mixins.BusinessEmailMixin, mixins.PhoneMixin, mixins.SupplierIDMixin, ORMModel
):
    name: Mapped[str_100]

    is_manufacturer: Mapped[Optional[bool]]
    year_established: Mapped[Optional[int]]
    number_of_employees: Mapped[Optional[int]]
    description: Mapped[Optional[text]]
    address: Mapped[Optional[text]]
    logo_url: Mapped[Optional[text]]
    business_sector: Mapped[Optional[str_100]]
    photo_url: Mapped[Optional[text]]

    supplier: Mapped[Optional[SupplierModel]] = relationship(back_populates="company")
