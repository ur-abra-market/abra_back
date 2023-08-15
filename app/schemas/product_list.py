from typing import List

from .core import ORMSchema
from .product import Product


class ProductList(ORMSchema):
    produts: List[Product] = []
    total_count: int = 0
