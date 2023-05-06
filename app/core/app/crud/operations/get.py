from __future__ import annotations

from typing import Any, Optional, Sequence

from sqlalchemy import Select as SQLAlchemySelect
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql.base import ExecutableOption

from .base import CRUDClassT, CrudOperation


class Get(CrudOperation[CRUDClassT]):
    def query(
        self,
        *models: Any,
        nested_select: Optional[Sequence[Any]] = None,
        where: Optional[Sequence[Any]] = None,
        filters: Optional[Sequence[Any]] = None,
        join: Optional[Sequence[Sequence[Any]]] = None,
        options: Optional[Sequence[ExecutableOption]] = None,
        offset: Optional[int] = None,
        limit: Optional[int] = None,
        order_by: Optional[Sequence[Any]] = None,
        group_by: Optional[Sequence[Any]] = None,
        having: Optional[Sequence[Any]] = None,
        select_from: Optional[Sequence[Any]] = None,
        correlate: bool = False,
        correlate_by: Optional[Sequence[Any]] = None,
    ) -> SQLAlchemySelect:
        models, nested_select, where, filters, join, options, order_by, group_by, having, select_from, correlate_by = self.transform(  # type: ignore[assignment]
            (self.__model__, *models),  # type: ignore[arg-type]
            nested_select,
            where,
            filters,
            join,
            options,
            order_by,
            group_by,
            having,
            select_from,
            correlate_by,
        )

        query = (
            select(*models, *nested_select)
            .where(*where)  # type: ignore[arg-type]
            .filter(*filters)
            .options(*options)
            .limit(limit)
            .order_by(*order_by)
            .group_by(*group_by)
            .having(*having)
            .select_from(*select_from)
        )

        for _join in join:
            query = query.join(*_join)

        if correlate:
            query = query.correlate(*correlate_by)

        if offset:
            query = query.filter(self.__model__.id > offset)  # type: ignore[union-attr]

        return query

    async def many_unique(
        self,
        *models: Any,
        session: AsyncSession,
        nested_select: Optional[Sequence[Any]] = None,
        where: Optional[Sequence[Any]] = None,
        filters: Optional[Sequence[Any]] = None,
        join: Optional[Sequence[Sequence[Any]]] = None,
        options: Optional[Sequence[ExecutableOption]] = None,
        offset: Optional[int] = None,
        limit: Optional[int] = None,
        order_by: Optional[Sequence[Any]] = None,
        group_by: Optional[Sequence[Any]] = None,
        having: Optional[Sequence[Any]] = None,
        select_from: Optional[Sequence[Any]] = None,
    ) -> Sequence[CRUDClassT]:
        cursor = await self.execute(
            session,
            *models,
            nested_select=nested_select,
            where=where,
            filters=filters,
            join=join,
            options=options,
            offset=offset,
            limit=limit,
            order_by=order_by,
            group_by=group_by,
            having=having,
            select_from=select_from,
        )

        return cursor.scalars().unique().all()

    async def many(
        self,
        *models: Any,
        session: AsyncSession,
        nested_select: Optional[Sequence[Any]] = None,
        where: Optional[Sequence[Any]] = None,
        filters: Optional[Sequence[Any]] = None,
        join: Optional[Sequence[Sequence[Any]]] = None,
        options: Optional[Sequence[ExecutableOption]] = None,
        offset: Optional[int] = None,
        limit: Optional[int] = None,
        order_by: Optional[Sequence[Any]] = None,
        group_by: Optional[Sequence[Any]] = None,
        having: Optional[Sequence[Any]] = None,
        select_from: Optional[Sequence[Any]] = None,
    ) -> Sequence[CRUDClassT]:
        cursor = await self.execute(
            session,
            *models,
            nested_select=nested_select,
            where=where,
            filters=filters,
            join=join,
            options=options,
            offset=offset,
            limit=limit,
            order_by=order_by,
            group_by=group_by,
            having=having,
            select_from=select_from,
        )

        return cursor.scalars().all()

    async def one(
        self,
        *models: Any,
        session: AsyncSession,
        nested_select: Optional[Sequence[Any]] = None,
        where: Optional[Sequence[Any]] = None,
        filters: Optional[Sequence[Any]] = None,
        join: Optional[Sequence[Sequence[Any]]] = None,
        options: Optional[Sequence[ExecutableOption]] = None,
        group_by: Optional[Sequence[Any]] = None,
        having: Optional[Sequence[Any]] = None,
        select_from: Optional[Sequence[Any]] = None,
    ) -> Optional[CRUDClassT]:
        cursor = await self.execute(
            session,
            *models,
            nested_select=nested_select,
            where=where,
            filters=filters,
            join=join,
            options=options,
            group_by=group_by,
            having=having,
            select_from=select_from,
        )

        return cursor.scalar()
