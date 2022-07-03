from pydantic import BaseModel, EmailStr
from typing import Union, List


# special responces to JSONResponces could be added using this:
# https://fastapi.tiangolo.com/advanced/additional-responses/

class RegisterIn(BaseModel):
    first_name: str
    last_name: str
    email: EmailStr
    phone: Union[str, None] = None
    password: str
    additional_info: Union[str, None] = None


class RegisterOut(BaseModel):
    result: str


class LoginIn(BaseModel):
    email: EmailStr
    password: str


class LoginOut(BaseModel):
    result: str


class ChangePasswordIn(BaseModel):
    email: EmailStr
    old_password: str
    new_password: str


class ChangePasswordOut(BaseModel):
    result: str


class EmailSchema(BaseModel):
    email: List[EmailStr]
