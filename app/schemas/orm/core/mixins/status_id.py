from __future__ import annotations

from pydantic import BaseModel


class StatusIDMixin(BaseModel):
    status_id: int
