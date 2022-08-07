from logic.consts import *
from pytz import timezone
import datetime
from fastapi_mail import ConnectionConfig, MessageSchema, FastMail
from os import getenv
from random import randint
from jose import jwt
from typing import Union, Any
from starlette.responses import JSONResponse


ALGORITHM = "HS256"
JWT_SECRET_KEY = getenv('JWT_SECRET_KEY')


conf = ConnectionConfig(
    MAIL_USERNAME=getenv("EMAIL"),
    MAIL_PASSWORD=getenv("PASS"),
    MAIL_FROM=getenv("EMAIL"),
    MAIL_PORT=587,
    MAIL_SERVER="smtp.gmail.com",
    MAIL_FROM_NAME="Desired Name",
    MAIL_TLS=True,
    MAIL_SSL=False,
    USE_CREDENTIALS=True
)


async def send_email(subject, recipient, body):
    message = MessageSchema(
        subject=subject,
        recipients=recipient,
        body=body,
        subtype="html"
    )
    fm = FastMail(conf)
    await fm.send_message(message=message)
    return JSONResponse(
        status_code=200,
        content={"result": "Message has been sent"}
    )


def create_access_token(subject: Union[str, Any]) -> str:
    to_encode = dict(
        sub=str(subject)
    )
    encoded_jwt = jwt.encode(to_encode, JWT_SECRET_KEY, ALGORITHM)
    return encoded_jwt


def get_current_user(token):
    token_data = jwt.decode(
        token, JWT_SECRET_KEY, algorithms=[ALGORITHM]
    )
    user = dict(email=token_data['sub'])
    return user


def get_rand_code():
    code = randint(100000, 999999)
    return code


class Dict(dict):
    __getattr__ = dict.get
    __setattr__ = dict.__setitem__
    __delattr__ = dict.__getitem__


def get_moscow_datetime():
    spb_timezone = timezone("Europe/Moscow")
    local_time = datetime.datetime.now()
    current_time = local_time.astimezone(spb_timezone)
    return current_time
