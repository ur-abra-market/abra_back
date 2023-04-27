from __future__ import annotations

from typing import Optional, Sequence, Tuple, cast

from sqlalchemy import Any, Result
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql.base import ExecutableOption

from exc import ColumnNotFound
from typing_ import DictStrAny

from .base import CRUDClassT, SequenceT
from .get import Get, raise_on_none_or_return


def dict_to_where(model: CRUDClassT, by: DictStrAny) -> Tuple[Any, ...]:
    try:
        return tuple(getattr(model, key) == value for key, value in by.items())
    except AttributeError as e:
        raise ColumnNotFound from e


class By(Get[CRUDClassT]):
    async def query(
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
        where = dict_to_where(model=self.__model__, by=kwargs)

        return await super(By, self).query(
            *models,
            session=session,
            where=where,  # type: ignore[arg-type]
            join=join,
            options=options,
            offset=offset,
            limit=limit,
            order_by=order_by,
            group_by=group_by,
            having=having,
            select_from=select_from,
        )

    async def many_unique(
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
    ) -> Sequence[CRUDClassT]:
        cursor = await self.query(
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

        return cast(
            Sequence[CRUDClassT],
            raise_on_none_or_return(
                data=cursor.scalars().unique().all(),
                raise_on_none=raise_on_none,
            ),
        )

    async def many(
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
    ) -> Sequence[CRUDClassT]:
        cursor = await self.query(
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

        return cast(
            Sequence[CRUDClassT],
            raise_on_none_or_return(
                data=cursor.scalars().all(),
                raise_on_none=raise_on_none,
            ),
        )

    async def one(
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
    ) -> Optional[CRUDClassT]:
        cursor = await self.query(
            *models,
            session=session,
            join=join,
            options=options,
            group_by=group_by,
            having=having,
            select_from=select_from,
            **kwargs,
        )

        return cast(
            Optional[CRUDClassT],
            raise_on_none_or_return(
                data=cursor.scalar(),
                raise_on_none=raise_on_none,
            ),
        )

    async def one_unique(
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
    ) -> Optional[CRUDClassT]:
        cursor = await self.query(
            *models,
            session=session,
            join=join,
            options=options,
            group_by=group_by,
            having=having,
            select_from=select_from,
            **kwargs,
        )

        return cast(
            Optional[CRUDClassT],
            raise_on_none_or_return(
                data=cursor.unique().scalar(),
                raise_on_none=raise_on_none,
            ),
        )
