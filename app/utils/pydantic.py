from __future__ import annotations

from typing import Any, Callable, Dict, Final, Iterable, Optional, Union

from pydantic import BaseModel
from pydantic import EmailStr as PydanticEmailStr


class EmailStr(PydanticEmailStr):
    @classmethod
    def validate(cls, value: Union[str]) -> str:
        return super(EmailStr, cls).validate(value=value).lower()


UPDATE_FORWARD_REFS: Final[str] = "update_forward_refs"


def update_forward_refs_helper(
    __all__: Iterable[str], __models__: Dict[str, Union[Any, BaseModel]]
) -> None:
    """
    Update forward references for given pydantic models.

    :param __all__: model names for updating
    :param __models__: all models
    :return: :class:`None`
    """

    for __entity_name__ in __all__:
        __entity__: Optional[Union[Any, BaseModel]] = __models__.get(__entity_name__, None)

        if hasattr(__entity__, UPDATE_FORWARD_REFS):
            __update_forwards_refs__: Callable[..., Any] = getattr(__entity__, UPDATE_FORWARD_REFS)
            __update_forwards_refs__(
                **{k: v for k, v in __models__.items() if k in __all__},
                **{"Optional": Optional},
            )
