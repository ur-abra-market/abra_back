from fastapi import APIRouter
from fastapi_mail import MessageSchema, FastMail
from .. import controller as c
from classes.enums import *
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


@register.post("/email")
async def send_confirmation_letter(email: EmailSchema) -> JSONResponse:
    message = MessageSchema(
        subject="Email confirmation letter",
        recipients=["t.kotenkova@list.ru"],
        body=html,
        subtype="html"
    )
    fm = FastMail(conf)
    await fm.send_message(message=message)
    return JSONResponse(
        status_code=200, content={"message": "email has been sent"}
    )