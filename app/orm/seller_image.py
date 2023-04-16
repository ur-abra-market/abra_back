from __future__ import annotations

from typing import TYPE_CHECKING, Optional

from sqlalchemy.orm import Mapped, relationship

from .core import ORMModel, mixins, text

if TYPE_CHECKING:
    from .seller import SellerModel


class SellerImageModel(mixins.SellerIDMixin, ORMModel):
    source_url: Mapped[text]
    thumbnail_url: Mapped[Optional[text]]

    seller: Mapped[Optional[SellerModel]] = relationship(back_populates="image")
