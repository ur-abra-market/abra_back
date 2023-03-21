"""
Tip: special responces to JSONResponces could be added using this:
https://fastapi.tiangolo.com/advanced/additional-responses/
"""
import datetime
from os import getenv
from typing import List, Optional, Any

from pydantic import BaseModel, EmailStr, validator

import app.api.consts as constants
from app.settings import *



class ResultOut(BaseModel):
    result: str


class OneImageOut(BaseModel):
    image_url: str = None
    serial_number: str = None


class ImagesOut(BaseModel):
    result: List[OneImageOut] = []


class SupplierOut(BaseModel):
    fullname: str
    grade_average: float
    total_deals: int = None
    value: Any
    period: Any


class ProductOut(BaseModel):
    """Product data."""

    id: int
    name: str
    description: str = ""
    total_orders: int
    grade_average: str
    datetime: datetime.date
    value_price: float = (
        0  # FIXME: remove default zero when there is engough data in DB
    )
    discount: float = 0
    with_discount: bool = False
    price_include_discount: float = 0
    min_quantity: int = 0
    is_favorite: bool = None

    @validator("discount", always=True, pre=True)
    def discount_validator(cls, v, values):
        return v or 0

    @validator("with_discount", always=True)
    def if_discount(cls, v, values) -> bool:
        dicount = values.get("discount", 0) or 0
        return dicount > 0

    @validator("price_include_discount", always=True)
    def price_with_discount(cls, v, values) -> float:
        if values["discount"]:
            return values["value_price"] - values["value_price"] * values["discount"]
        else:
            return values["value_price"]


class AllProductDataOut(BaseModel):
    """All data of one product with images and supplier info."""

    product: ProductOut
    supplier: Optional[SupplierOut] = None
    images: List[ImagesOut] = []


class ProductPaginationOut(BaseModel):
    """All products of a page."""

    total_products: int = 0
    result: List[AllProductDataOut] = []


class ListOfProducts(BaseModel):
    result: List[ProductOut]


class ListOfProductsOut(BaseModel):
    result: List[dict]