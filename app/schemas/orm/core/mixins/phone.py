from __future__ import annotations

from typing import Optional

from pydantic import BaseModel


class PhoneMixin(BaseModel):
    phone: Optional[str] = None
