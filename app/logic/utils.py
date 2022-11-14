import os
import logging
import hashlib
import datetime
from pytz import timezone
from random import randint
from jose import jwt
from typing import Union, Any
from fastapi_mail import ConnectionConfig, MessageSchema, FastMail
from fastapi import HTTPException, UploadFile, status
from starlette.responses import JSONResponse
import imghdr
import boto3

from app.logic.consts import *


ALGORITHM = "HS256"
JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY')


conf = ConnectionConfig(
    MAIL_USERNAME=os.getenv("EMAIL_USERNAME"),
    MAIL_PASSWORD=os.getenv("EMAIL_PASS"),
    MAIL_FROM=os.getenv("EMAIL_USERNAME"),
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
        html=body,
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
    return token_data["sub"]


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


async def upload_file_to_s3(bucket, file: UploadFile):
    bucket = os.getenv("AWS_BUCKET")
    _, file_extension = os.path.splitext(file.filename)
    contents = await file.read()
    filehash = hashlib.md5(contents)
    filename = str(filehash.hexdigest())
    await file.seek(0)

    # Validate file if it is image
    if not imghdr.what("", h=contents):
        logging.error("File is not an image: '%s'", file.filename)
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="NOT_IMAGE")

    # Upload file to S3
    s3_client = boto3.client(
        service_name="s3"
    )
    key = f"{filename[:2]}/{filename}{file_extension}"
    s3_client.upload_fileobj(file.file, bucket, key)
    url = f"https://{bucket}.s3.amazonaws.com/{key}"
    logging.info("File is uploaded to S3 by path: '%s'", f"s3://{bucket}/{key}")
    return url