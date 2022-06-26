import json
from const.const import *
from pytz import timezone
import datetime
from passlib.context import CryptContext


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
