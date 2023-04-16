from __future__ import annotations

from typing import (
    TYPE_CHECKING,
    Any,
    Callable,
    Dict,
    Generic,
    List,
    Optional,
    Sequence,
    TypeAlias,
    TypeVar,
    Union,
)

from pydantic import BaseConfig, BaseModel, validator
from pydantic.generics import GenericModel
from pydantic.utils import GetterDict
from sqlalchemy import inspect
from sqlalchemy.orm.attributes import instance_state

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

        return super(ExcludeNone, self).dict(  # type: ignore
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

        return super(ExcludeNone, self).json(  # type: ignore
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
        smart_union = True

    @validator("*", pre=True)
    def empty_sequence_to_none(
        cls, v: Union[Any, Sequence[Any]]
    ) -> Optional[Union[Any, Sequence[Any]]]:
        if not isinstance(v, Sequence):
            return v
        return v if len(v) else None


class IgnoreLazyGetterDict(GetterDict):
    def __getitem__(self, key: str) -> Any:
        try:
            if self._is_lazy_loaded(key):
                return None

            return getattr(self._obj, key)
        except AttributeError as e:
            raise KeyError(key) from e

    def get(self, key: Any, default: Any = None) -> Any:
        if self._is_relationship(key) and self._is_lazy_loaded(key):
            return None

        return getattr(self._obj, key, default)

    def _is_lazy_loaded(self, key: Any) -> bool:
        return key in instance_state(self._obj).unloaded

    def _is_relationship(self, key: Any) -> bool:
        relationship_keys = [r.key for r in inspect(self._obj.__class__).relationships]
        return key in relationship_keys


class ApplicationORMSchema(ApplicationSchema):
    class Config(BaseConfig):
        orm_mode = True
        getter_dict = IgnoreLazyGetterDict


ErrorT: TypeAlias = Union[
    str,
    List[str],
    List[Dict[str, Any]],
    Dict[str, Any],
]
ResponseT = TypeVar("ResponseT", bound=Any)


class ApplicationResponse(ExcludeNone, GenericModel, Generic[ResponseT]):
    class Config:
        orm_mode = True
        smart_union = True

    ok: bool
    result: Optional[ResponseT] = None
    detail: Optional[str] = None
    error: Optional[ErrorT] = None
    error_code: Optional[int] = None
