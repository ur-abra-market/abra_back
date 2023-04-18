from __future__ import annotations

from typing import Dict, Generic, Optional, Sequence, Tuple, TypeVar, cast

from sqlalchemy import Any, Result
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql.base import ExecutableOption

from .base import BaseOperation, SequenceT

ClassT = TypeVar("ClassT")


class GetBy(BaseOperation[ClassT], Generic[ClassT]):
    def _to_where(self, get_by: Dict[str, Any]) -> Tuple[Any, ...]:
        return tuple(getattr(self.__model__, key) == value for key, value in get_by.items())

    async def get_by_impl(
        self,
        *models: Any,
        session: AsyncSession,
        join: Optional[SequenceT[SequenceT[Any]]] = None,
        options: Optional[SequenceT[ExecutableOption]] = None,
        offset: Optional[int] = None,
        limit: Optional[int] = None,
        order_by: Optional[SequenceT[Any]] = None,
        group_by: Optional[SequenceT[Any]] = None,
        having: Optional[SequenceT[Any]] = None,
        select_from: Optional[SequenceT[Any]] = None,
        **kwargs: Any,
    ) -> Result[Any]:
        where = self._to_where(get_by=kwargs)

        return await self.get_impl(  # type: ignore
            *models,
            session=session,
            where=where,
            join=join,
            options=options,
            offset=offset,
            limit=limit,
            order_by=order_by,
            group_by=group_by,
            having=having,
            select_from=select_from,
        )

    async def get_many_unique_by(
        self,
        *models: Any,
        session: AsyncSession,
        join: Optional[SequenceT[SequenceT[Any]]] = None,
        options: Optional[SequenceT[ExecutableOption]] = None,
        offset: Optional[int] = None,
        limit: Optional[int] = None,
        order_by: Optional[SequenceT[Any]] = None,
        group_by: Optional[SequenceT[Any]] = None,
        having: Optional[SequenceT[Any]] = None,
        select_from: Optional[SequenceT[Any]] = None,
        **kwargs: Any,
    ) -> Sequence[ClassT]:
        cursor = await self.get_by_impl(
            *models,
            session=session,
            join=join,
            options=options,
            offset=offset,
            limit=limit,
            order_by=order_by,
            group_by=group_by,
            having=having,
            select_from=select_from,
            **kwargs,
        )

        return cursor.scalars().unique().all()  # type: ignore[no-any-return]

    async def get_many_by(
        self,
        *models: Any,
        session: AsyncSession,
        join: Optional[SequenceT[SequenceT[Any]]] = None,
        options: Optional[SequenceT[ExecutableOption]] = None,
        offset: Optional[int] = None,
        limit: Optional[int] = None,
        order_by: Optional[SequenceT[Any]] = None,
        group_by: Optional[SequenceT[Any]] = None,
        having: Optional[SequenceT[Any]] = None,
        select_from: Optional[SequenceT[Any]] = None,
        **kwargs: Any,
    ) -> Sequence[ClassT]:
        cursor = await self.get_by_impl(
            *models,
            session=session,
            join=join,
            options=options,
            offset=offset,
            limit=limit,
            order_by=order_by,
            group_by=group_by,
            having=having,
            select_from=select_from,
            **kwargs,
        )

        return cursor.scalars().all()  # type: ignore[no-any-return]

    async def get_one_by(
        self,
        *models: Any,
        session: AsyncSession,
        join: Optional[SequenceT[SequenceT[Any]]] = None,
        options: Optional[SequenceT[ExecutableOption]] = None,
        group_by: Optional[SequenceT[Any]] = None,
        having: Optional[SequenceT[Any]] = None,
        select_from: Optional[SequenceT[Any]] = None,
        **kwargs: Any,
    ) -> Optional[ClassT]:
        cursor = await self.get_by_impl(
            *models,
            session=session,
            join=join,
            options=options,
            group_by=group_by,
            having=having,
            select_from=select_from,
            **kwargs,
        )

        return cast(ClassT, cursor.scalar())

    async def get_one_unique_by(
        self,
        *models: Any,
        session: AsyncSession,
        join: Optional[SequenceT[SequenceT[Any]]] = None,
        options: Optional[SequenceT[ExecutableOption]] = None,
        group_by: Optional[SequenceT[Any]] = None,
        having: Optional[SequenceT[Any]] = None,
        select_from: Optional[SequenceT[Any]] = None,
        **kwargs: Any,
    ) -> Optional[ClassT]:
        cursor = await self.get_by_impl(
            *models,
            session=session,
            join=join,
            options=options,
            group_by=group_by,
            having=having,
            select_from=select_from,
            **kwargs,
        )

        return cast(ClassT, cursor.unique().scalar())
