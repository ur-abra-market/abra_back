import datetime as dt
from typing import Optional

from .schema import ApplicationSchema
from .variation_value_to_product import VariationValueToProduct


class ProductPrice(ApplicationSchema):
    variation_value_to_product_id: int
    price: float
    discount: float
    start_date: dt.datetime
    end_date: dt.datetime
    min_quantity: int

    product_variation_value: Optional[VariationValueToProduct] = None
