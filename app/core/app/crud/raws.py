from __future__ import annotations

from typing import Any, List, Optional, Sequence, Union

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql.base import ExecutableOption
from sqlalchemy.sql.dml import ReturningDelete, ReturningInsert, ReturningUpdate

from typing_ import DictStrAny

from .crud import CRUD
from .operations import CRUDClassT, Delete, Get, Insert, SequenceT, Update


class _Get(Get[CRUDClassT]):
    async def many_unique(
        self,
        *models: Any,
        session: AsyncSession,
        nested_select: Optional[SequenceT[Any]] = None,
        where: Optional[SequenceT[Any]] = None,
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
            join=join,
            options=options,
            group_by=group_by,
            having=having,
            select_from=select_from,
        )

        return cursor.mappings().unique().one_or_none()


class _Delete(Delete[CRUDClassT]):
    def query(self, where: Optional[Any] = None) -> ReturningDelete[Any]:
        raise AttributeError("Not supported in raws")


class _Insert(Insert[CRUDClassT]):
    def query(self, values: Union[DictStrAny, List[DictStrAny]]) -> ReturningInsert[Any]:
        raise AttributeError("Not supported in raws")


class _Update(Update[CRUDClassT]):
    def query(
        self, values: Union[DictStrAny, List[DictStrAny]], where: Optional[Any] = None
    ) -> ReturningUpdate[Any]:
        raise AttributeError("Not supported in raws")


class Raws(CRUD[None]):
    def __init__(self) -> None:
        super(Raws, self).__init__(
            get=_Get,
            insert=_Insert,
            update=_Update,
            delete=_Delete,
        )
