from __future__ import annotations

from typing import Optional

from .schema import ApplicationSchema


class JWT(ApplicationSchema):
    user_id: Optional[int] = None
