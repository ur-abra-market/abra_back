from __future__ import annotations

from typing import (
    TYPE_CHECKING,
    Any,
    Generic,
    Iterable,
    List,
    Optional,
    Sequence,
    TypeVar,
)

from sqlalchemy import Join, Result, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql.base import ExecutableOption

from .base import BaseOperation

ClassT = TypeVar("ClassT")


class Get(BaseOperation, Generic[ClassT]):
    if TYPE_CHECKING:
        model: ClassT

    async def get_impl(
        self,
        *models: Any,
        session: AsyncSession,
        where: Optional[Sequence[Any]] = None,
        join: Optional[Sequence[Any]] = None,
        options: Optional[Sequence[ExecutableOption]] = None,
        offset: Optional[int] = None,
        limit: Optional[int] = None,
        order_by: Optional[Sequence[Any]] = None,
        group_by: Optional[Sequence[Any]] = None,
        having: Optional[Sequence[Any]] = None,
        select_from: Optional[Sequence[Join]] = None,
    ) -> Result[ClassT]:
        models, where, join, options, order_by, group_by, having, select_from = self.transform(
            (*models, self.model), where, join, options, order_by, group_by, having, select_from
        )

        query = (
            select(*models)
            .where(*where)
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

    async def get_many(
        self,
        *models: Any,
        session: AsyncSession,
        where: Optional[Sequence[Any]] = None,
        join: Optional[Sequence[Iterable[Any, Any]]] = None,
        options: Optional[Sequence[ExecutableOption]] = None,
        offset: Optional[int] = None,
        limit: Optional[int] = None,
        order_by: Optional[Sequence[Any]] = None,
        group_by: Optional[Sequence[Any]] = None,
        having: Optional[Sequence[Any]] = None,
        select_from: Optional[Sequence[Join]] = None,
    ) -> Optional[List[ClassT]]:
        cursor = await self.get_impl(
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

        return cursor.scalars().all() or None

    async def get_many_unique(
        self,
        *models: Any,
        session: AsyncSession,
        where: Optional[Sequence[Any]] = None,
        join: Optional[Sequence[Any]] = None,
        options: Optional[Sequence[ExecutableOption]] = None,
        offset: Optional[int] = None,
        limit: Optional[int] = None,
        order_by: Optional[Sequence[Any]] = None,
        group_by: Optional[Sequence[Any]] = None,
        having: Optional[Sequence[Any]] = None,
        select_from: Optional[Sequence[Join]] = None,
    ) -> Optional[List[ClassT]]:
        cursor = await self.get_impl(
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

        return cursor.scalars().unique().all() or None

    async def get_one(
        self,
        *models: Any,
        session: AsyncSession,
        where: Optional[Sequence[Any]] = None,
        join: Optional[Sequence[Any]] = None,
        options: Optional[Sequence[ExecutableOption]] = None,
        group_by: Optional[Sequence[Any]] = None,
        having: Optional[Sequence[Any]] = None,
        select_from: Optional[Sequence[Join]] = None,
    ) -> Optional[ClassT]:
        cursor = await self.get_impl(
            *models,
            session=session,
            where=where,
            join=join,
            options=options,
            group_by=group_by,
            having=having,
            select_from=select_from,
        )

        return cursor.scalar()

    async def get_one_unique(
        self,
        *models: Any,
        session: AsyncSession,
        where: Optional[Sequence[Any]] = None,
        join: Optional[Sequence[Any]] = None,
        options: Optional[Sequence[ExecutableOption]] = None,
        group_by: Optional[Sequence[Any]] = None,
        having: Optional[Sequence[Any]] = None,
        select_from: Optional[Sequence[Join]] = None,
    ) -> Optional[ClassT]:
        cursor = await self.get_impl(
            *models,
            session=session,
            where=where,
            join=join,
            options=options,
            group_by=group_by,
            having=having,
            select_from=select_from,
        )

        return cursor.unique().scalar()
