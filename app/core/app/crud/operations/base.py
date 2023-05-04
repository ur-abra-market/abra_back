from __future__ import annotations

import abc
from typing import (
    Any,
    Generator,
    Generic,
    Optional,
    Sequence,
    Tuple,
    Type,
    TypeVar,
    Union,
    cast,
)

from sqlalchemy import Executable, Result
from sqlalchemy.ext.asyncio import AsyncSession

CRUDClassT = TypeVar("CRUDClassT")
AliasCRUDClassT = Union[Type[CRUDClassT], Type[None]]

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
    use_on_default: Type[Tuple[Any]],
) -> SequenceT[InSequenceT]:
    return (
        cast(SequenceT[InSequenceT], use_on_default())  # type: ignore[misc]
        if sequence is None
        else klass(i for i in sequence if i is not None)  # type: ignore[misc]
    )


class _BuildMixin:
    _USE_DEFAULT: Type[Tuple[Any]] = tuple  # type: ignore[assignment]

    def transform(
        self, *sequences: Optional[SequenceT[InSequenceT]]
    ) -> Tuple[SequenceT[InSequenceT], ...]:
        return tuple(
            _filter(
                klass=sequence.__class__,
                sequence=sequence,
                use_on_default=self._USE_DEFAULT,
            )
            for sequence in sequences
        )


class _ABCQueryBuilder(abc.ABC):
    @abc.abstractmethod
    def query(self, *args: Any, **kwargs: Any) -> Executable:
        ...


class CrudOperation(_ABCQueryBuilder, _BuildMixin, abc.ABC, Generic[CRUDClassT]):
    def __init__(self, model: AliasCRUDClassT) -> None:
        self.__model__ = model

    async def execute(self, session: AsyncSession, *args: Any, **kwargs: Any) -> Result[Any]:
        return await session.execute(self.query(*args, **kwargs))
