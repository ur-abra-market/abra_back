"""
Tip: special responces to JSONResponces could be added using this:
https://fastapi.tiangolo.com/advanced/additional-responses/
"""

from pydantic import BaseModel, EmailStr
from typing import List, Optional
from os import getenv
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


class ListOfProductsOut(BaseModel):
    result: List[dict]


class SellerUserData(BaseModel):
    first_name: str
    last_name: str
    email: EmailStr
    phone_number: str


class SellerUserNotification(BaseModel):
    on_discount: Optional[bool]
    on_order_updates: Optional[bool]
    on_order_reminders: Optional[bool]
    on_stock_again: Optional[bool]
    on_product_is_cheaper: Optional[bool]
    on_your_favorites_new: Optional[bool]
    on_account_support: Optional[bool]


class SellerUserAdress(BaseModel):
    country: Optional[str]
    area: Optional[str]
    city: Optional[str]
    street: Optional[str]
    building: Optional[str]
    appartment: Optional[str]
    postal_code: Optional[str]
