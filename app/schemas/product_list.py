from typing import List

from .product import Product
from .schema import ApplicationSchema


class ProductList(ApplicationSchema):
    total_count: int
    products: List[Product] = None
