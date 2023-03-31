from typing import List

from ..schema import ApplicationSchema
from .product_info import ProductInfo


class ProductList(ApplicationSchema):
    total: int = 0
    products: List[ProductInfo] = []
