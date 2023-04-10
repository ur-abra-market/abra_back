from __future__ import annotations

from pydantic import BaseModel, EmailStr


class EmailMixin(BaseModel):
    email: EmailStr
