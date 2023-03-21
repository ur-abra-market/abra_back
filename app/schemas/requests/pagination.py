from pydantic import Field

from ..schema import ApplicationSchema


class PaginationQuery(ApplicationSchema):
    offset: int = Field(0, ge=0, le=100)
    limit: int = Field(100, ge=0, le=100)
