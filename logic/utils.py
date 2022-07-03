import json
from const.const import *
from pytz import timezone
import datetime
from passlib.context import CryptContext
from fastapi_mail import ConnectionConfig
from dotenv import load_dotenv
from os import getenv


load_dotenv()


conf = ConnectionConfig(
    MAIL_USERNAME = getenv("USERNAME"),
    MAIL_PASSWORD = getenv("PASS"),
    MAIL_FROM = getenv("EMAIL"),
    MAIL_PORT = 587,
    MAIL_SERVER = "smtp.mail.ru",
    MAIL_FROM_NAME="Desired Name",
    MAIL_TLS = True,
    MAIL_SSL = False,
    USE_CREDENTIALS = True
)


html = """
<p>!!!Пока временное содержание письма!!!</p> 
"""

pwd_context = CryptContext(
        schemes=["pbkdf2_sha256"],
        default="pbkdf2_sha256",
        pbkdf2_sha256__default_rounds=30000
)


def hash_password(password):
    return pwd_context.hash(password)


def check_hashed_password(password, hashed):
    return pwd_context.verify(password, hashed)



class Dict(dict):
    __getattr__ = dict.get
    __setattr__ = dict.__setitem__
    __delattr__ = dict.__getitem__


def callback(data):
    d = json.dumps(data)
    return d


def get_callback(callback_data):
    return json.loads(callback_data)

    
def get_moscow_datetime():
    spb_timezone = timezone("Europe/Moscow")
    local_time = datetime.datetime.now()
    current_time = local_time.astimezone(spb_timezone)
    return current_time
