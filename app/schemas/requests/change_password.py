from pydantic import Field

from ..schema import ApplicationSchema
from .metadata import PASSWORD_REGEX


class ChangePassword(ApplicationSchema):
    old_password: str
    new_password: str = Field(..., regex=PASSWORD_REGEX)
