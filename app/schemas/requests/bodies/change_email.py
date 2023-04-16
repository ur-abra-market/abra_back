from __future__ import annotations

from typing import Any, Dict

from pydantic import EmailStr, validator

from ...schema import ApplicationSchema


class ChangeEmail(ApplicationSchema):
    new_email: EmailStr
    confirm_email: EmailStr

    @validator("new_email")
    def emails_are_same(cls, v: str, values: Dict[str, Any]) -> str:
        if v != values.get("confirm_email"):
            raise ValueError("emails not same")
        return v
