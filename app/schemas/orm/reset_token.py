from __future__ import annotations

import uuid

from pydantic import EmailStr

from .schema import ORMSchema


class ResetToken(ORMSchema):
    email: EmailStr
    user_id: int
    reset_code: uuid.UUID
    status: bool
