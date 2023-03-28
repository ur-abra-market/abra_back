from pydantic import EmailStr, Field

from ...schema import ApplicationSchema
from .metadata import PASSWORD_REGEX


class Register(ApplicationSchema):
    email: EmailStr
    password: str = Field(..., regex=PASSWORD_REGEX)
