from __future__ import annotations

import datetime as dt
from typing import Optional

from pydantic import BaseModel


class TimestampMixin(BaseModel):
    datetime: dt.datetime
    updated_at: Optional[dt.datetime] = None
