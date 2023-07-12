from __future__ import annotations

from typing import TYPE_CHECKING, Optional

from sqlalchemy.orm import Mapped, relationship

from .core import ORMModel, mixins, types

if TYPE_CHECKING:
    from .company import CompanyModel


class CompanyImageModel(mixins.CompanyIDMixin, ORMModel):
    url: Mapped[Optional[types.text]]

    company: Mapped[Optional[CompanyModel]] = relationship(back_populates="images")
