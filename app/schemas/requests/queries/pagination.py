from __future__ import annotations

from pydantic import Field

from ...schema import ApplicationSchema


class Pagination(ApplicationSchema):
    offset: int = Field(0, ge=0)
    limit: int = Field(100, ge=0, le=100)
