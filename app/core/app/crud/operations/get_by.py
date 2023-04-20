from __future__ import annotations

from typing import Dict, Generic, Optional, Sequence, Tuple, TypeVar

from sqlalchemy import Any, Result
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql.base import ExecutableOption

from exc import ColumnNotFound

from .base import SequenceT
from .get import Get, raise_on_none_or_return

ClassT = TypeVar("ClassT")


def dict_to_where(model: ClassT, get_by: Dict[str, Any]) -> Tuple[Any]:
    try:
        return tuple(getattr(model, key) == value for key, value in get_by.items())  # type: ignore[return-value]
    except AttributeError as e:
        raise ColumnNotFound from e


class GetBy(Get[ClassT], Generic[ClassT]):
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
        where = dict_to_where(model=self.__model__, get_by=kwargs)

        return await self.get_impl(
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
        raise_on_none: bool = False,
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

        return raise_on_none_or_return(
            data=cursor.scalars().unique().all(),
            raise_on_none=raise_on_none,
        )  # type: ignore[return-value]

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
        raise_on_none: bool = False,
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

        return raise_on_none_or_return(
            data=cursor.scalars().all(),
            raise_on_none=raise_on_none,
        )  # type: ignore[return-value]

    async def get_one_by(
        self,
        *models: Any,
        session: AsyncSession,
        join: Optional[SequenceT[SequenceT[Any]]] = None,
        options: Optional[SequenceT[ExecutableOption]] = None,
        group_by: Optional[SequenceT[Any]] = None,
        having: Optional[SequenceT[Any]] = None,
        select_from: Optional[SequenceT[Any]] = None,
        raise_on_none: bool = False,
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

        return raise_on_none_or_return(
            data=cursor.scalar(),
            raise_on_none=raise_on_none,
        )

    async def get_one_unique_by(
        self,
        *models: Any,
        session: AsyncSession,
        join: Optional[SequenceT[SequenceT[Any]]] = None,
        options: Optional[SequenceT[ExecutableOption]] = None,
        group_by: Optional[SequenceT[Any]] = None,
        having: Optional[SequenceT[Any]] = None,
        select_from: Optional[SequenceT[Any]] = None,
        raise_on_none: bool = False,
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

        return raise_on_none_or_return(
            data=cursor.unique().scalar(),
            raise_on_none=raise_on_none,
        )
