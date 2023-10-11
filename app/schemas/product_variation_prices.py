import datetime as dt
from typing import Optional

from .schema import ApplicationSchema
from .variation_value_to_product import VariationValueToProduct


class ProductVariationPrice(ApplicationSchema):
    product_id: int
    value: float
    multiplier: float
    discount: float
    start_date: dt.datetime
    end_date: dt.datetime
    min_quantity: int

    product_variation_value: Optional[VariationValueToProduct] = None
