from __future__ import annotations

from sqlalchemy.orm import Mapped

from .core import ORMModel, mixins, types


class VariationValueImageModel(mixins.VariationValueToProductIDMixin, ORMModel):
    image_url: Mapped[types.text]
    thumbnail_url: Mapped[types.text]
