from __future__ import annotations

from typing import TYPE_CHECKING, Any, Callable, Generic, Optional, TypeVar, Union

from pydantic import BaseConfig, BaseModel
from pydantic.generics import GenericModel

if TYPE_CHECKING:
    from pydantic.typing import AbstractSetIntStr, DictStrAny, MappingIntStrAny


class ExcludeNone:
    def dict(
        self,
        *,
        include: Optional[Union[AbstractSetIntStr, MappingIntStrAny]] = None,
        exclude: Optional[Union[AbstractSetIntStr, MappingIntStrAny]] = None,
        by_alias: bool = False,
        skip_defaults: Optional[bool] = None,
        exclude_unset: bool = False,
        exclude_defaults: bool = False,
        exclude_none: bool = False,
    ) -> DictStrAny:
        exclude_none = True

        return super(ExcludeNone, self).dict(
            include=include,
            exclude=exclude,
            by_alias=by_alias,
            skip_defaults=skip_defaults,
            exclude_unset=exclude_unset,
            exclude_defaults=exclude_defaults,
            exclude_none=exclude_none,
        )

    def json(
        self,
        *,
        include: Optional[Union[AbstractSetIntStr, MappingIntStrAny]] = None,
        exclude: Optional[Union[AbstractSetIntStr, MappingIntStrAny]] = None,
        by_alias: bool = False,
        skip_defaults: Optional[bool] = None,
        exclude_unset: bool = False,
        exclude_defaults: bool = False,
        exclude_none: bool = False,
        encoder: Optional[Callable[[Any], Any]] = None,
        models_as_dict: bool = True,
        **dumps_kwargs: Any,
    ) -> str:
        exclude_none = True

        return super(ExcludeNone, self).json(
            include=include,
            exclude=exclude,
            by_alias=by_alias,
            skip_defaults=skip_defaults,
            exclude_unset=exclude_unset,
            exclude_defaults=exclude_defaults,
            exclude_none=exclude_none,
            encoder=encoder,
            models_as_dict=models_as_dict,
            **dumps_kwargs,
        )


class ApplicationSchema(ExcludeNone, BaseModel):
    class Config(BaseConfig):
        allow_population_by_field_name = True


class ApplicationORMSchema(ApplicationSchema):
    class Config(BaseConfig):
        orm_mode = True


ResponseT = TypeVar("ResponseT", bound=Any)


class ApplicationResponse(ExcludeNone, GenericModel, Generic[ResponseT]):
    ok: bool
    result: Optional[ResponseT] = None
    error: Optional[str] = None
