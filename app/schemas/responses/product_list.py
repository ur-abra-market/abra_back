from typing import List

from ..orm import Product
from ..schema import ApplicationSchema


class ProductList(ApplicationSchema):
    total: int = 0
    products: List[Product] = []
