from __future__ import annotations

from typing import TYPE_CHECKING, Optional
from sqlalchemy.orm import Mapped, relationship

from .core import ORMModel, mixins

if TYPE_CHECKING:
    from .variation_value import VariationValueModel


class VariationValueToProductModel(mixins.ProductIDMixin, mixins.VariationValueIDMixin, ORMModel):
    ...
