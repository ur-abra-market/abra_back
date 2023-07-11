from __future__ import annotations

from pydantic import Field, validator

from metadata import PASSWORD_REGEX
from typing_ import DictStrAny

from .schema import ApplicationSchema


class ResetPasswordUpload(ApplicationSchema):
    new_password: str
    confirm_password: str = Field(..., max_length=30, regex=PASSWORD_REGEX)

    @validator("confirm_password")
    def password_are_same(cls, v: str, values: DictStrAny) -> str:
        if v != values.get("new_password"):
            raise ValueError("passwords not same")
        return v
