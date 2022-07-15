from fastapi import APIRouter
from fastapi_mail import MessageSchema, FastMail
from .. import controller as c
from classes.response_models import *
from logic.utils import *
from starlette.responses import JSONResponse


register = APIRouter()


@register.get("/")
async def register_main():
    # there we will ask a type of user (sellers, suppliers)
    return 'Register page'
    

@register.post("/{user_type}/", response_model=RegisterOut)
async def register_user(user_type: str, user_data: RegisterIn):
    result = await c.register_user(user_type=user_type, user_data=user_data)
    return result


@register.post("/email/")
async def send_confirmation_letter(email: MyEmail) -> JSONResponse:
    subject = "Email confirmation"
    recipient = [email.email]
    message = "confirmation link"
    result = await c.send_email(subject, recipient, message)
    return result


@register.get("/email_confirmation")
async def check_email_code(email: EmailSchema, code: int):
    result = await c.check_confirm_code(email, code)
    return result