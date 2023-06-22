from __future__ import annotations

from pydantic import Field, validator

from metadata import PASSWORD_REGEX
from typing_ import DictStrAny

from ...schema import ApplicationSchema


class ChangePassword(ApplicationSchema):
    old_password: str
    new_password: str = Field(..., max_length=30, regex=PASSWORD_REGEX)

    @validator("old_password")
    def password_are_not_same(cls, v: str, values: DictStrAny) -> str:
        if v == values.get("new_password"):
            raise ValueError("same passwords")
        return v
