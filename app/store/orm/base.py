from __future__ import annotations

from typing import Any, Dict, Generic, List, Optional, Sequence, TypeVar, Union

from sqlalchemy import Executable, Join, Result, insert, select, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql.base import ExecutableOption

from orm.core import ORMModel

ClassT = TypeVar("ClassT", bound=ORMModel)


class _BaseORM:
    def _transform(self, *sequences: Optional[Sequence[Any]]) -> List[List[Any]]:
        return [[] if sequence is None else sequence for sequence in sequences]


class _Get(_BaseORM, Generic[ClassT]):
    async def get_impl(
        self,
        session: AsyncSession,
        where: Optional[Sequence[Any]] = None,
        join: Optional[Sequence[Join]] = None,
        options: Optional[Sequence[ExecutableOption]] = None,
        offset: Optional[int] = None,
        limit: Optional[int] = None,
    ) -> Result[ClassT]:
        where, join, options = self._transform(where, join, options)

        return await self.execute(
            session,
            select(self.model)
            .where(*where)
            .options(*options)
            .offset(offset)
            .limit(limit)
            .select_from(*join),
        )

    async def get_many(
        self,
        session: AsyncSession,
        where: Optional[Sequence[Any]] = None,
        join: Optional[Sequence[Join]] = None,
        options: Optional[Sequence[ExecutableOption]] = None,
        offset: Optional[int] = None,
        limit: Optional[int] = None,
    ) -> Optional[List[ClassT]]:
        cursor = await self.get_impl(
            session=session,
            where=where,
            join=join,
            options=options,
            offset=offset,
            limit=limit,
        )
        return cursor.scalars().all() or None

    async def get_one(
        self,
        session: AsyncSession,
        where: Optional[Sequence[Any]] = None,
        join: Optional[Sequence[Join]] = None,
        options: Optional[Sequence[ExecutableOption]] = None,
    ) -> ClassT:
        cursor = await self.get_impl(
            session=session,
            where=where,
            join=join,
            options=options,
        )
        return cursor.scalar()


class _GetNew(Generic[ClassT]):
    async def get_by_id(
        self,
        session: AsyncSession,
        id: Any,
        where: Optional[Sequence[Any]] = None,
        join: Optional[Sequence[Join]] = None,
        options: Optional[Sequence[ExecutableOption]] = None,
    ) -> ClassT:
        model = self.model
        where = [model.id == id] if where is None else list(where)

        return super(_GetNew, self).get_one(
            session=session,
            where=where,
            join=join,
            options=options,
        )


class _Insert(_BaseORM, Generic[ClassT]):
    async def insert(
        self,
        session: AsyncSession,
        values: Union[Dict[str, Any], List[Dict[str, Any]]],
    ) -> Union[List[ClassT], ClassT]:
        multi = not isinstance(values, Dict)

        cursor = await self.execute(
            session, insert(self.model).values(values).returning(self.model)
        )
        if multi:
            return cursor.scalars().all()
        return cursor.scalar()


class _Update(_BaseORM, Generic[ClassT]):
    async def update(
        self,
        session: AsyncSession,
        values: Union[Dict[str, Any], List[Dict[str, Any]]],
        where: Optional[Sequence[Any]] = None,
    ) -> Union[List[ClassT], ClassT]:
        multi = not isinstance(values, Dict)
        where = self._transform(where)

        cursor = await self.execute(
            session, update(self.model).values(values).where(*where).returning(self.model)
        )
        if multi:
            return cursor.scalars().all()
        return cursor.scalar()


class ORMAccessor(
    _Get[ClassT], _GetNew[ClassT], _Insert[ClassT], _Update[ClassT], Generic[ClassT]
):
    def __init__(self, model: ClassT) -> None:
        self.model = model

    async def execute(self, session: AsyncSession, statement: Executable) -> Result[ClassT]:
        cursor = await session.execute(statement)
        return cursor
