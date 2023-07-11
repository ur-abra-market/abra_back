from __future__ import annotations

from pydantic import Field

from metadata import PASSWORD_REGEX
from utils.pydantic import EmailStr

from .schema import ApplicationSchema


class RegisterUpload(ApplicationSchema):
    email: EmailStr
    password: str = Field(..., max_length=30, regex=PASSWORD_REGEX)
