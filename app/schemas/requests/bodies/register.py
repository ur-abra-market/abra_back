from __future__ import annotations

from pydantic import EmailStr, Field

from ...schema import ApplicationSchema
from .metadata import PASSWORD_REGEX


class Register(ApplicationSchema):
    email: EmailStr
    password: str = Field(..., max_length=30, regex=PASSWORD_REGEX)
