from __future__ import annotations

from typing import TYPE_CHECKING, Optional

from sqlalchemy.orm import Mapped, relationship

from .core import ORMModel, mixins, text

if TYPE_CHECKING:
    from .company import CompanyModel


class CompanyImageModel(mixins.CompanyIDMixin, ORMModel):
    url: Mapped[Optional[text]]

    company: Mapped[Optional[CompanyModel]] = relationship(back_populates="images")
