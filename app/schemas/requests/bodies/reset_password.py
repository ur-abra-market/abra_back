from __future__ import annotations

from typing import Any, Dict

from pydantic import Field, validator

from ...schema import ApplicationSchema
from .metadata import PASSWORD_REGEX


class ResetPassword(ApplicationSchema):
    new_password: str
    confirm_password: str = Field(..., max_length=30, regex=PASSWORD_REGEX)

    @validator("confirm_password")
    def password_are_same(cls, v: str, values: Dict[str, Any]) -> str:
        if v != values.get("new_password"):
            raise ValueError("passwords not same")
        return v
