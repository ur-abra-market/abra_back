from __future__ import annotations

from pydantic import BaseModel


class UserIDMixin(BaseModel):
    user_id: int
