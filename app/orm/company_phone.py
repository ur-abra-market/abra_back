from __future__ import annotations

from typing import TYPE_CHECKING, Optional

from sqlalchemy.orm import Mapped, relationship

from .core import ORMModel, mixins

if TYPE_CHECKING:
    from .company_image import CompanyModel
    from .country import CountryModel


class CompanyPhoneModel(mixins.PhoneMixin, mixins.CompanyIDMixin, ORMModel):
    company: Mapped[Optional[CompanyModel]] = relationship(back_populates="phone")
    country: Mapped[Optional[CountryModel]] = relationship()
