from typing import Generic, Optional, TypeVar, Any

from pydantic import BaseConfig, BaseModel
from pydantic.generics import GenericModel


class ApplicationSchema(BaseModel):
    class Config(BaseConfig):
        allow_population_by_field_name = True


class ApplicationORMSchema(ApplicationSchema):
    class Config(BaseConfig):
        orm_mode = True


ResponseT = TypeVar("ResponseT", bound=Any)


class ApplicationResponse(GenericModel, Generic[ResponseT]):
    ok: bool
    result: Optional[ResponseT] = None
    error: Optional[str] = None
