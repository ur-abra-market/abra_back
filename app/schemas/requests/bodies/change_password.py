from typing import Any, Dict

from pydantic import Field, validator

from ...schema import ApplicationSchema
from .metadata import PASSWORD_REGEX


class ChangePassword(ApplicationSchema):
    old_password: str
    new_password: str = Field(..., regex=PASSWORD_REGEX)

    @validator("old_password")
    def password_are_same(cls, v: str, values: Dict[str, Any]) -> str:
        if v == values.get("new_password"):
            raise ValueError("Same passwords")
        return v
