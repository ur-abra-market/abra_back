from __future__ import annotations

from sqlalchemy.orm import Mapped

from ..constraints import variation_value_to_product_fk
from ..types import variation_value_to_product_fk_type


class VariationValueToProductIDMixin:
    product_variation_value_id: Mapped[
        variation_value_to_product_fk_type
    ] = variation_value_to_product_fk
