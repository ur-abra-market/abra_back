from __future__ import annotations

from typing import TYPE_CHECKING, Optional

from sqlalchemy.orm import Mapped, relationship

from .core import ORMModel, mixins, types

if TYPE_CHECKING:
    from .seller import SellerModel


class SellerImageModel(mixins.SellerIDMixin, ORMModel):
    source_url: Mapped[Optional[types.text]]
    thumbnail_url: Mapped[Optional[types.text]]

    seller: Mapped[Optional[SellerModel]] = relationship(back_populates="image")
