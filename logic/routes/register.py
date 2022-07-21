from fastapi import APIRouter
from .. import controller as c
from classes.response_models import *
from logic.utils import *
from starlette.responses import JSONResponse


register = APIRouter()
   

@register.post("/email-confirmation/")
async def send_confirmation_letter(email: MyEmail) -> JSONResponse:
    result = await c.send_confirmation_email(email.email)
    return result


@register.post("/email-confirmation-result/")
async def receive_confirmation_result(token: ConfirmationToken) -> JSONResponse:
    result = await c.receive_registration_result(token.token)
    return result


@register.post("/{user_type}/", summary='WORKS: User registration.', response_model=ResultOut)
async def register_user(user_type: str, user_data: RegisterIn):
    result = await c.register_user(user_type=user_type, user_data=user_data)
    return result
