import json
from datetime import date
from typing import List
import typing
from const.const import *
from random import randint
import re
from pytz import timezone
import datetime


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