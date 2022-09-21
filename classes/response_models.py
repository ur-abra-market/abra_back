from multiprocessing.managers import BaseManager
from pydantic import BaseModel, EmailStr
from typing import Union, List, Optional
from os import getenv


# special responces to JSONResponces could be added using this:
# https://fastapi.tiangolo.com/advanced/additional-responses/

class Settings(BaseModel):
    authjwt_secret_key: str = getenv('JWT_SECRET_KEY')
    # Configure application to store and get JWT from cookies
    authjwt_token_location: set = {"cookies"}
    # Only allow JWT cookies to be sent over https
    authjwt_cookie_secure: bool = True
    # Enable csrf double submit protection. default is True
    authjwt_cookie_csrf_protect: bool = True
    # Change to 'lax' in production to make your website more secure from CSRF Attacks, default is None
    authjwt_cookie_samesite: str = 'lax'

# universal response (if just "result" was returned)
class ResultOut(BaseModel):
    result: str


class RegisterIn(BaseModel):
    email: EmailStr
    password: str


class LoginIn(BaseModel):
    email: EmailStr
    password: str


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
    product_review_photo: Union[str, None] = None
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


class PropertiesDict(BaseModel):
    key: str
    value: str
    optional_value: Optional[str]


class SizesDict(BaseModel):
    size: str
    count: int


class TypesDict(BaseModel):
    color: str
    sizes: List[SizesDict]


class MainProductInfo(BaseModel):
    product_name:str
    description: str
    properties: List[PropertiesDict]
    types: List[TypesDict]


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
    license_number: str


class SupplierCompanyData(BaseModel):
    logo_url: str
    shop_name: str
    business_sector: str
    is_manufacturer: int
    year_established: Optional[int]
    number_of_employees: Optional[int]
    description: Optional[str]
    photo_url: Optional[List[str]]
    phone: Optional[str]
    business_email: Optional[EmailStr]
    adress: Optional[str]


class SupplierCountry(BaseModel):
    country: str