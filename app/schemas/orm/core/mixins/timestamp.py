from __future__ import annotations

import datetime as dt
from typing import Optional


class TimestampMixin:
    datetime: dt.datetime
    updated_at: Optional[dt.datetime] = None
