import json
from const.const import *
from pytz import timezone
import datetime
from fastapi_mail import ConnectionConfig
from dotenv import load_dotenv
from os import getenv
from random import randint
from . import controller as c


load_dotenv()

conf = ConnectionConfig(
    MAIL_USERNAME = getenv("EMAIL"),
    MAIL_PASSWORD = getenv("PASS"),
    MAIL_FROM = getenv("EMAIL"),
    MAIL_PORT = 587,
    MAIL_SERVER = "smtp.gmail.com",
    MAIL_FROM_NAME="Desired Name",
    MAIL_TLS = True,
    MAIL_SSL = False,
    USE_CREDENTIALS = True
)


def get_rand_code():
    code = randint(100000, 999999)
    return code


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
