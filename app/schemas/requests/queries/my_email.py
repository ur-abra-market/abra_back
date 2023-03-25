from pydantic import EmailStr

from ...schema import ApplicationSchema


class MyEmail(ApplicationSchema):
    email: EmailStr
