from typing import Any, Dict

from pydantic import Field, validator

from ..schema import ApplicationSchema
from .metadata import PASSWORD_REGEX


class ChangePassword(ApplicationSchema):
    old_password: str
    new_password: str = Field(..., regex=PASSWORD_REGEX)

    @validator("new_password")
    def passwords_match(cls, v: str, values: Dict[str, Any]) -> str:
        if "old_password" in values and v != values["old_password"]:
            raise ValueError("Passwords do not match")
        return v
