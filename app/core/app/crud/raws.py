from __future__ import annotations

from typing import Any, List, Optional, Sequence, Union, cast

from sqlalchemy import Select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql.base import ExecutableOption
from sqlalchemy.sql.dml import ReturningDelete, ReturningInsert, ReturningUpdate

from typing_ import DictStrAny

from .crud import CRUD
from .operations import (
    By,
    CRUDClassT,
    Delete,
    Get,
    Insert,
    SequenceT,
    Update,
    raise_on_none_or_return,
)


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
        raise_on_none: bool = False,
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

        return cast(
            Sequence[Any],
            raise_on_none_or_return(
                data=cursor.mappings().unique().all(),
                raise_on_none=raise_on_none,
            ),
        )

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
        raise_on_none: bool = False,
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

        return cast(
            Sequence[Any],
            raise_on_none_or_return(
                data=cursor.mappings().all(),
                raise_on_none=raise_on_none,
            ),
        )

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
        raise_on_none: bool = False,
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

        return raise_on_none_or_return(
            data=cursor.mappings().one_or_none(),
            raise_on_none=raise_on_none,
        )

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
        raise_on_none: bool = False,
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

        return raise_on_none_or_return(
            data=cursor.mappings().unique().one_or_none(),
            raise_on_none=raise_on_none,
        )


class _By(By[CRUDClassT]):
    def query(
        self,
        *models: Any,
        nested_select: Optional[SequenceT[Any]] = None,
        join: Optional[SequenceT[SequenceT[Any]]] = None,
        options: Optional[SequenceT[ExecutableOption]] = None,
        offset: Optional[int] = None,
        limit: Optional[int] = None,
        order_by: Optional[SequenceT[Any]] = None,
        group_by: Optional[SequenceT[Any]] = None,
        having: Optional[SequenceT[Any]] = None,
        select_from: Optional[SequenceT[Any]] = None,
        **kwargs: Any,
    ) -> Select:
        raise AttributeError("Not supported in raws")


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
            by=_By,
            insert=_Insert,
            update=_Update,
            delete=_Delete,
        )
