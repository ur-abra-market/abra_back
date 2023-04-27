from __future__ import annotations

import abc
from typing import (
    Any,
    Final,
    Generator,
    Generic,
    Optional,
    Sequence,
    Tuple,
    Type,
    TypeAlias,
    TypeVar,
    Union,
    cast,
)

from sqlalchemy import Result

CRUDClassT = TypeVar("CRUDClassT")
AliasCRUDClassT: TypeAlias = Union[Type[CRUDClassT], Type[None]]

InSequenceT = TypeVar("InSequenceT", bound=Any)


# noinspection PyUnusedLocal
class SequenceT(abc.ABC, Sequence[InSequenceT]):
    def __init__(
        self,
        iterable: Union[
            Generator[InSequenceT, None, None], Optional[Sequence[InSequenceT]]
        ] = None,
    ) -> None:
        ...


def _filter(
    klass: Union[Type[SequenceT[InSequenceT]], Type[None]],
    sequence: Optional[SequenceT[InSequenceT]] = None,
    *,
    use_on_default: Tuple[Any],
) -> SequenceT[InSequenceT]:
    return (
        cast(SequenceT[InSequenceT], use_on_default)
        if sequence is None
        else klass(i for i in sequence if i is not None)  # type: ignore[misc]
    )


class CrudOperation(abc.ABC, Generic[CRUDClassT]):
    _USE_DEFAULT: Final[Tuple[Any]] = ()  # type: ignore[assignment]

    def __init__(self, model: AliasCRUDClassT) -> None:
        self.__model__ = model

    def transform(
        self,
        *sequences: Optional[SequenceT[InSequenceT]],
    ) -> Tuple[SequenceT[InSequenceT], ...]:
        return tuple(
            _filter(
                klass=sequence.__class__,
                sequence=sequence,
                use_on_default=self._USE_DEFAULT,
            )
            for sequence in sequences
        )

    @abc.abstractmethod
    async def query(self, *args: Any, **kwargs: Any) -> Result[Any]:
        ...
