from typing import List

from ..schema import ApplicationORMSchema
from ..orm import (
    Supplier,
    Product,
    ProductImage,
    ProductPrice,
)


class ProductInfo(ApplicationORMSchema):
    product: Product
    price: ProductPrice
    supplier: Supplier
    images: List[ProductImage] = []
