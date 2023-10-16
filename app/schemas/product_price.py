import datetime as dt
from typing import Optional

from .core import ORMSchema
from .variation_value_to_product import VariationValueToProduct


class ProductPrice(ORMSchema):
    product_id: int
    value: float
    discount: float
    start_date: dt.datetime
    end_date: dt.datetime
    min_quantity: int

    product_variation_value: Optional[VariationValueToProduct] = None
