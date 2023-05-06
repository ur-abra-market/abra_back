from __future__ import annotations

import abc
from typing import Any, Generic, Optional, Sequence, Tuple, Type, TypeVar, cast

from sqlalchemy import Executable
from sqlalchemy.ext.asyncio import AsyncResult, AsyncSession

CRUDClassT = TypeVar("CRUDClassT")


def _filter(
    klass: Type[Any],
    sequence: Optional[Sequence[Any]] = None,
    *,
    use_on_default: Type[Tuple[Any]],
) -> Sequence[Any]:
    return (
        cast(Sequence[Any], use_on_default())  # type: ignore[misc]
        if sequence is None
        else klass(i for i in sequence if i is not None)  # type: ignore[misc]
    )


class _BuildMixin:
    _USE_DEFAULT: Type[Tuple[Any]] = tuple  # type: ignore[assignment]

    def transform(self, *sequences: Optional[Sequence[Any]]) -> Tuple[Sequence[Any], ...]:
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


class CRUDOperation(_ABCQueryBuilder, _BuildMixin, abc.ABC, Generic[CRUDClassT]):
    def __init__(self, model: Type[Any]) -> None:
        self.__model__ = model

    async def one(
        self,
        *args: Any,
        session: AsyncSession,
        **kwargs: Any,
    ) -> Optional[CRUDClassT]:
        cursor = await self.execute(session, *args, **kwargs)

        return await cursor.scalars().one_or_none()

    async def many(
        self,
        *args: Any,
        session: AsyncSession,
        **kwargs: Any,
    ) -> Sequence[CRUDClassT]:
        cursor = await self.execute(session, *args, **kwargs)

        return await cursor.scalars().all()

    async def many_unique(
        self,
        *args: Any,
        session: AsyncSession,
        **kwargs: Any,
    ) -> Sequence[CRUDClassT]:
        cursor = await self.execute(session, *args, **kwargs)

        return await cursor.unique().scalars().all()

    async def execute(self, session: AsyncSession, *args: Any, **kwargs: Any) -> AsyncResult[Any]:
        return await session.stream(self.query(*args, **kwargs))
