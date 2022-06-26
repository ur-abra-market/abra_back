from pydantic import BaseModel, EmailStr
from typing import Union


class RegisterIn(BaseModel):
    first_name: str
    last_name: str
    phone_number: Union[str, None] = None
    email: EmailStr
    password: str


class RegisterOut(BaseModel):
    result: str


class LoginIn(BaseModel):
    email: EmailStr
    password: str


class LoginOut(BaseModel):
    result: str


class PasswordIn(BaseModel):
    email: EmailStr
    old_password: str
    new_password: str


class PasswordOut(BaseModel):
    result: str