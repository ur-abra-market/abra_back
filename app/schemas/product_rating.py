from typing import Dict, Optional

from .product import Product
from .schema import ApplicationSchema


class ProductRating(ApplicationSchema):
    product: Product = None
    feedbacks: Optional[Dict] = None
