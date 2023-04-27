from __future__ import annotations

from typing import Any, Optional, Sequence, cast

from sqlalchemy import Result, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql.base import ExecutableOption

from exc import ResultRequired

from .base import CRUDClassT, CrudOperation, SequenceT


def raise_on_none_or_return(data: Any, raise_on_none: bool = False) -> Any:
    if isinstance(data, Sequence) and not len(data) and raise_on_none:
        raise ResultRequired
    if data is None and raise_on_none:
        raise ResultRequired

    return data


class Get(CrudOperation[CRUDClassT]):
    async def query(
        self,
        *models: Any,
        session: AsyncSession,
        where: Optional[SequenceT[Any]] = None,
        join: Optional[SequenceT[SequenceT[Any]]] = None,
        options: Optional[SequenceT[ExecutableOption]] = None,
        offset: Optional[int] = None,
        limit: Optional[int] = None,
        order_by: Optional[SequenceT[Any]] = None,
        group_by: Optional[SequenceT[Any]] = None,
        having: Optional[SequenceT[Any]] = None,
        select_from: Optional[SequenceT[Any]] = None,
    ) -> Result[Any]:
        models, where, join, options, order_by, group_by, having, select_from = self.transform(  # type: ignore[assignment]
            (*models, self.__model__),  # type: ignore[arg-type]
            where,
            join,
            options,
            order_by,
            group_by,
            having,
            select_from,
        )

        query = (
            select(*models)
            .where(*where)  # type: ignore[arg-type]
            .options(*options)
            .offset(offset)
            .limit(limit)
            .order_by(*order_by)
            .group_by(*group_by)
            .having(*having)
            .select_from(*select_from)
        )

        for _join in join:
            query = query.join(*_join)

        return await session.execute(query)

    async def many_unique(
        self,
        *models: Any,
        session: AsyncSession,
        where: Optional[SequenceT[Any]] = None,
        join: Optional[SequenceT[SequenceT[Any]]] = None,
        options: Optional[SequenceT[ExecutableOption]] = None,
        offset: Optional[int] = None,
        limit: Optional[int] = None,
        order_by: Optional[SequenceT[Any]] = None,
        group_by: Optional[SequenceT[Any]] = None,
        having: Optional[SequenceT[Any]] = None,
        select_from: Optional[SequenceT[Any]] = None,
        raise_on_none: bool = False,
    ) -> Sequence[CRUDClassT]:
        cursor = await self.query(
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
        where: Optional[SequenceT[Any]] = None,
        join: Optional[SequenceT[SequenceT[Any]]] = None,
        options: Optional[SequenceT[ExecutableOption]] = None,
        offset: Optional[int] = None,
        limit: Optional[int] = None,
        order_by: Optional[SequenceT[Any]] = None,
        group_by: Optional[SequenceT[Any]] = None,
        having: Optional[SequenceT[Any]] = None,
        select_from: Optional[SequenceT[Any]] = None,
        raise_on_none: bool = False,
    ) -> Sequence[CRUDClassT]:
        cursor = await self.query(
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
        where: Optional[SequenceT[Any]] = None,
        join: Optional[SequenceT[SequenceT[Any]]] = None,
        options: Optional[SequenceT[ExecutableOption]] = None,
        group_by: Optional[SequenceT[Any]] = None,
        having: Optional[SequenceT[Any]] = None,
        select_from: Optional[SequenceT[Any]] = None,
        raise_on_none: bool = False,
    ) -> Optional[CRUDClassT]:
        cursor = await self.query(
            *models,
            session=session,
            where=where,
            join=join,
            options=options,
            group_by=group_by,
            having=having,
            select_from=select_from,
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
        where: Optional[SequenceT[Any]] = None,
        join: Optional[SequenceT[SequenceT[Any]]] = None,
        options: Optional[SequenceT[ExecutableOption]] = None,
        group_by: Optional[SequenceT[Any]] = None,
        having: Optional[SequenceT[Any]] = None,
        select_from: Optional[SequenceT[Any]] = None,
        raise_on_none: bool = False,
    ) -> Optional[CRUDClassT]:
        cursor = await self.query(
            *models,
            session=session,
            where=where,
            join=join,
            options=options,
            group_by=group_by,
            having=having,
            select_from=select_from,
        )

        return cast(
            Optional[CRUDClassT],
            raise_on_none_or_return(
                data=cursor.unique().scalar(),
                raise_on_none=raise_on_none,
            ),
        )
