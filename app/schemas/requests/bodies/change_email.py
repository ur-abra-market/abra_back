from __future__ import annotations

from pydantic import EmailStr, validator

from typing_ import DictStrAny

from ...schema import ApplicationSchema


class ChangeEmail(ApplicationSchema):
    new_email: EmailStr
    confirm_email: EmailStr

    @validator("new_email")
    def emails_are_same(cls, v: str, values: DictStrAny) -> str:
        if v != values.get("confirm_email"):
            raise ValueError("emails not same")
        return v
