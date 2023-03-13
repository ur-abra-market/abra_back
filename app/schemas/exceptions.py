from pydantic import BaseModel, BaseConfig

from app.common.enums import ErrorCodes



class SimpleApiError(BaseModel):
    """A simple model for HTTP errors without payload."""

    code: ErrorCodes
    message: str

    class Config(BaseConfig):
        orm_mode = True
        allow_population_by_field_name = True


