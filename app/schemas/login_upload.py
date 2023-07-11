from __future__ import annotations

from pydantic import EmailStr

from .schema import ApplicationSchema


class LoginUpload(ApplicationSchema):
    email: EmailStr
    password: str
