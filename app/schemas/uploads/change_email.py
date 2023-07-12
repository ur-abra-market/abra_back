from __future__ import annotations

from pydantic import validator

from typing_ import DictStrAny
from utils.pydantic import EmailStr

from ..schema import ApplicationSchema


class ChangeEmailUpload(ApplicationSchema):
    confirm_email: EmailStr
    new_email: EmailStr

    @validator("new_email")
    def emails_are_same(cls, v: str, values: DictStrAny) -> str:
        if v != values.get("confirm_email"):
            raise ValueError("emails not same")
        return v
