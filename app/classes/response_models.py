"""
Tip: special responces to JSONResponces could be added using this:
https://fastapi.tiangolo.com/advanced/additional-responses/
"""
from os import getenv
import datetime

from pydantic import BaseModel, EmailStr
from typing import List, Optional

from app.settings import *


class Settings(BaseModel):
    authjwt_secret_key: str = getenv("JWT_SECRET_KEY", "")
    # Configure application to store and get JWT from cookies
    authjwt_token_location: set = {"cookies"}
    # Only allow JWT cookies to be sent over https
    authjwt_cookie_secure: bool = COOKIE_SECURE
    # Enable csrf double submit protection. default is True
    authjwt_cookie_csrf_protect: bool = IS_CSRF_TOKEN_ENABLED
    # Change to 'lax' in production to make your website more secure from CSRF Attacks, default is None
    authjwt_cookie_samesite: str = COOKIE_SAMESITE
    authjwt_cookie_domain = COOKIE_DOMAIN
    authjwt_cookie_max_age: int = 86400


class ResultOut(BaseModel):
    result: str


class ProductOut(BaseModel):
    id: int
    name: str
    description: str
    total_orders: int
    grade_average: str
    date_added: datetime.date
    with_discount: int
    price_include_discount: str
    min_quantity: int
    value_price: float
    is_favorite: bool
    # image_url: str


class ListOfProducts(BaseModel):
    result: List[ProductOut]


class ListOfProductsOut(BaseModel):
    result: List[dict]
