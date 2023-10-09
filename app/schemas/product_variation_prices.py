from typing import Optional

from .schema import ApplicationSchema
from .variation_value_to_product import VariationValueToProduct


class ProductVariationPrice(ApplicationSchema):
    product_id: int
    price: float
    discount: float

    product_variation_value: Optional[VariationValueToProduct] = None
