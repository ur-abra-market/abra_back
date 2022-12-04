import logging
from multiprocessing.managers import BaseManager
from pydantic import BaseModel, EmailStr
from typing import Union, List, Optional
from os import getenv
from app.settings import *


# special responces to JSONResponces could be added using this:
# https://fastapi.tiangolo.com/advanced/additional-responses/

class Settings(BaseModel):
    authjwt_secret_key: str = getenv('JWT_SECRET_KEY')
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


class GetRoleOut(BaseModel):
    is_supplier: bool

# universal response (if just "result" was returned)


class ResultOut(BaseModel):
    result: str


class RegisterIn(BaseModel):
    email: EmailStr
    password: str


class LoginIn(BaseModel):
    email: EmailStr
    password: str


class LoginOut(BaseModel):
    result: str
    is_supplier: int


class ChangePasswordIn(BaseModel):
    old_password: str
    new_password: str


class MyEmail(BaseModel):
    email: str


class EmailSchema(BaseModel):
    email: List[EmailStr]


class ListOfProductsOut(BaseModel):
    result: List[dict]


class CategoryPath(BaseModel):
    path: str


class ResetPassword(BaseModel):
    email: str
    # reset_password_token: str
    new_password: str
    confirm_password: str


class ConfirmationToken(BaseModel):
    token: str


class ImagesOut(BaseModel):
    image_url: str
    serial_number: str


class SearchesOut(BaseModel):
    search_query: str
    datetime: str


class ProductReviewIn(BaseModel):
    product_review_photo: Union[List[str], None]
    product_review_text: str
    product_review_grade: int


class GradeOut(BaseModel):
    grade: dict
    grade_details: List[dict]


class ReactionIn(BaseModel):
    reaction: bool


class SupplierInfo(BaseModel):
    first_name: str
    last_name: str
    country: str
    phone: str
    tax_number: int


class SupplierAccountInfo(BaseModel):
    logo_url: Optional[str] = None
    shop_name: str
    business_sector: str
    is_manufacturer: int
    year_established: Optional[int] = None
    number_of_emploees: Optional[int] = None
    description: Optional[str] = None
    photo_url: Optional[str] = None
    business_phone: Optional[str] = None
    business_email: Optional[EmailStr] = None
    company_address: Optional[str] = None


class ProductIdOut(BaseModel):
    product_id: int


class ResultListOut(BaseModel):
    result: List[str]

# start - add product models


class PropertiesDict(BaseModel):
    name: str
    value: str
    optional_value: Optional[str]


class VariationsChildDict(BaseModel):
    name: str
    value: str
    count: int


class VariationsDict(BaseModel):
    name: str
    value: str
    count: Optional[int]
    childs: Optional[List[VariationsChildDict]]


class ProductInfo(BaseModel):
    product_name: str
    category_id: int
    description: Optional[str]


class PersonalInfo(BaseModel):
    first_name: str
    last_name: str
    country: str
    personal_number: str
    license_number: str


class BusinessProfile(BaseModel):
    logo_url: str
    shop_name: str
    business_sector: str
    is_manufacturer: int
    year_established: int
    number_of_employees: int
    description: str
    photo_url: List[str]
    phone: str
    business_email: EmailStr
    adress: str


class AccountDetails(BaseModel):
    email: EmailStr
    password: str


class SupplierAccountInfoOut(BaseModel):
    personal_info: PersonalInfo
    business_profile: BusinessProfile
    account_details: AccountDetails


class SupplierUserData(BaseModel):
    first_name: str
    last_name: Optional[str]
    phone: str


class SupplierLicense(BaseModel):
    license_number: int


class SupplierCompanyData(BaseModel):
    logo_url: str
    name: str
    business_sector: str
    is_manufacturer: int
    year_established: Optional[int]
    number_of_employees: Optional[int]
    description: Optional[str]
    photo_url: Optional[List[str]]
    phone: Optional[str]
    business_email: Optional[EmailStr]
    address: Optional[str]


class SupplierCountry(BaseModel):
    country: str


class ProductPrices(BaseModel):
    value: float
    quantity: int
# end - add product models


class CompanyInfo(BaseModel):
    name: str
    logo_url: str


class UpdateUserNotification(BaseModel):
    on_discount: bool = None
    on_order_updates: bool = None
    on_order_reminders: bool = None
    on_stock_again: bool = None
    on_product_is_cheaper: bool = None
    on_your_favorites_new: bool = None
    on_account_support: bool = None


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


# class DeleteProducts(BaseModel):
#     products: List[int]

# class PaginationIn(BaseModel):
#     page_num: int = 1
#     page_size: int = 10
#     category_id: Optional[int] = None
#     bottom_price: Optional[int] = None
#     top_price: Optional[int] = None
#     with_discount: Optional[bool] = False
#     sort_type: str = 'rating'
#     ascending: bool = False

