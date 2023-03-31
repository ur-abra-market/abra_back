from datetime import datetime
from functools import partial
import pytz

# TODO: вынести tz в энвы или константы
TIMEZONE = pytz.timezone("Europe/Moscow")

current_datetime_tz = partial(datetime.now, tz=TIMEZONE)
