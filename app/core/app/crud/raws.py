from __future__ import annotations

from typing import Any, Optional, Sequence

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql.base import ExecutableOption

from .crud import CRUD
from .operations import CRUDClassT, Get, SequenceT


class _Get(Get[CRUDClassT]):
    async def many_unique(
        self,
        *models: Any,
        session: AsyncSession,
        nested_select: Optional[SequenceT[Any]] = None,
        where: Optional[SequenceT[Any]] = None,
        filters: Optional[SequenceT[Any]] = None,
        join: Optional[SequenceT[SequenceT[Any]]] = None,
        options: Optional[SequenceT[ExecutableOption]] = None,
        offset: Optional[int] = None,
        limit: Optional[int] = None,
        order_by: Optional[SequenceT[Any]] = None,
        group_by: Optional[SequenceT[Any]] = None,
        having: Optional[SequenceT[Any]] = None,
        select_from: Optional[SequenceT[Any]] = None,
    ) -> Sequence[Any]:
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

        return cursor.mappings().unique().all()

    async def get_many(
        self,
        *models: Any,
        session: AsyncSession,
        nested_select: Optional[SequenceT[Any]] = None,
        where: Optional[SequenceT[Any]] = None,
        filters: Optional[SequenceT[Any]] = None,
        join: Optional[SequenceT[SequenceT[Any]]] = None,
        options: Optional[SequenceT[ExecutableOption]] = None,
        offset: Optional[int] = None,
        limit: Optional[int] = None,
        order_by: Optional[SequenceT[Any]] = None,
        group_by: Optional[SequenceT[Any]] = None,
        having: Optional[SequenceT[Any]] = None,
        select_from: Optional[SequenceT[Any]] = None,
    ) -> Sequence[Any]:
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

        return cursor.mappings().all()

    async def get_one(
        self,
        *models: Any,
        session: AsyncSession,
        nested_select: Optional[SequenceT[Any]] = None,
        where: Optional[SequenceT[Any]] = None,
        filters: Optional[SequenceT[Any]] = None,
        join: Optional[SequenceT[SequenceT[Any]]] = None,
        options: Optional[SequenceT[ExecutableOption]] = None,
        group_by: Optional[SequenceT[Any]] = None,
        having: Optional[SequenceT[Any]] = None,
        select_from: Optional[SequenceT[Any]] = None,
    ) -> Optional[Any]:
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

        return cursor.mappings().one_or_none()

    async def get_one_unique(
        self,
        *models: Any,
        session: AsyncSession,
        nested_select: Optional[SequenceT[Any]] = None,
        where: Optional[SequenceT[Any]] = None,
        filters: Optional[SequenceT[Any]] = None,
        join: Optional[SequenceT[SequenceT[Any]]] = None,
        options: Optional[SequenceT[ExecutableOption]] = None,
        group_by: Optional[SequenceT[Any]] = None,
        having: Optional[SequenceT[Any]] = None,
        select_from: Optional[SequenceT[Any]] = None,
    ) -> Optional[Any]:
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

        return cursor.mappings().unique().one_or_none()


class Raws(CRUD[None]):
    def __init__(self) -> None:
        super(Raws, self).__init__(get=_Get)
