from __future__ import annotations

from typing import TypeVar, Generic, List, Sequence, Any, Optional

from sqlalchemy import Result, Executable, select, Join
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql.base import ExecutableOption

from app.orm.core import ORMModel

ClassT = TypeVar("ClassT", bound=ORMModel)


class _BaseORM:
    def __init__(self, orm_accessor: ORMAccessor) -> None:
        self.orm_accessor = orm_accessor


class _Getter(_BaseORM, Generic[ClassT]):
    async def get_impl(
        self,
        session: AsyncSession,
        where: Optional[Sequence[Any]] = None,
        join: Optional[Join] = None,
        options: Optional[Sequence[ExecutableOption]] = None,
        offset: Optional[int] = None,
        limit: Optional[int] = None,
    ) -> Result[ClassT]:
        if where is None:
            where = []
        if join is None:
            join = []
        if options is None:
            options = []

        return await self.orm_accessor.execute(
            session,
            select(self.orm_accessor.model)
            .where(*where)
            .options(*options)
            .offset(offset)
            .limit(limit)
            .select_from(join)
        )

    async def get_many(
        self,
        session: AsyncSession,
        where: Optional[Sequence[Any]] = None,
        join: Optional[Join] = None,
        options: Optional[Sequence[ExecutableOption]] = None,
        offset: Optional[int] = None,
        limit: Optional[int] = None,
    ) -> List[ClassT]:
        cursor = await self.get_impl(
            session=session,
            where=where,
            join=join,
            options=options,
            offset=offset,
            limit=limit,
        )
        return cursor.scalars().all()

    async def get_one(
        self,
        session: AsyncSession,
        where: Optional[Sequence[Any]] = None,
        join: Optional[Join] = None,
        options: Optional[Sequence[ExecutableOption]] = None,
        offset: Optional[int] = None,
        limit: Optional[int] = None,
    ) -> ClassT:
        cursor = await self.get_impl(
            session=session,
            where=where,
            join=join,
            options=options,
            offset=offset,
            limit=limit,
        )
        return cursor.scalar()


class ORMAccessor(_Getter[ClassT], Generic[ClassT]):
    def __init__(self, model: ClassT) -> None:
        super(ORMAccessor, self).__init__(self)

        self.model = model

    async def execute(self, session: AsyncSession, statement: Executable) -> Result[ClassT]:
        cursor = await session.execute(statement)
        return cursor
