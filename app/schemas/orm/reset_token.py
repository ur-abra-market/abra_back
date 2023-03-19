from __future__ import annotations

from app.schemas.orm.schema import ORMSchema
from pydantic import EmailStr


class ResetToken(ORMSchema):
    email: EmailStr
    user_id: int
    reset_code: str
    status: bool
