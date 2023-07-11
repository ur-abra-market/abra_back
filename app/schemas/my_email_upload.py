from __future__ import annotations

from utils.pydantic import EmailStr

from .schema import ApplicationSchema


class MyEmailUpload(ApplicationSchema):
    email: EmailStr
