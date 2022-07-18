from fastapi import APIRouter
from fastapi_mail import MessageSchema, FastMail
from .. import controller as c
from classes.response_models import *
from logic.utils import *
from starlette.responses import JSONResponse


register = APIRouter()
   

@register.post("/email/",
               summary='WORKS: Send confirmation letter with link to user email during registration process.',
               response_model=ResultOut)
async def send_confirmation_letter(email: MyEmail):
    subject = "Email confirmation"
    recipient = [email.email]
    body = "<b>confirmation link</b>"
    result = await c.send_email(subject, recipient, body)
    return result


@register.post("/{user_type}/", summary='WORKS: User registration.', response_model=ResultOut)
async def register_user(user_type: str, user_data: RegisterIn):
    result = await c.register_user(user_type=user_type, user_data=user_data)
    return result
