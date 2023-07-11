from __future__ import annotations

from pydantic import BaseModel

from utils.pydantic import EmailStr


class EmailMixin(BaseModel):
    email: EmailStr
