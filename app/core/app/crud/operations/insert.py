from __future__ import annotations

from typing import Any, List, Optional, Sequence, Union, cast

from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql.dml import ReturningInsert

from typing_ import DictStrAny

from .base import CRUDClassT, CrudOperation


class Insert(CrudOperation[CRUDClassT]):
    def query(self, values: Union[DictStrAny, List[DictStrAny]]) -> ReturningInsert[Any]:
        query = insert(self.__model__).values(values).returning(self.__model__)

        return query  # noqa

    async def many(self, session: AsyncSession, values: List[DictStrAny]) -> Sequence[CRUDClassT]:
        cursor = await self.execute(session, values=values)

        return cast(Sequence[CRUDClassT], cursor.scalars().all())

    async def one(self, session: AsyncSession, values: DictStrAny) -> Optional[CRUDClassT]:
        cursor = await self.execute(session, values=values)

        return cast(CRUDClassT, cursor.scalar())
