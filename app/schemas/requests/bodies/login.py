from __future__ import annotations

from pydantic import EmailStr

from ...schema import ApplicationSchema


class Login(ApplicationSchema):
    email: EmailStr
    password: str

    class Config:
        schema_extra = {
            "example": {
                "email": "supplier@mail.ru",
                "password": "Password1!",
            }
        }
