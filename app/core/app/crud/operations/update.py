from __future__ import annotations

from typing import Any, List, Optional, Sequence, Union, cast

from sqlalchemy import Result, update
from sqlalchemy.ext.asyncio import AsyncSession

from typing_ import DictStrAny

from .base import CRUDClassT, CrudOperation


class Update(CrudOperation[CRUDClassT]):
    async def query(
        self,
        session: AsyncSession,
        values: Union[DictStrAny, List[DictStrAny]],
        where: Optional[Any] = None,
    ) -> Result[Any]:
        query = (
            update(self.__model__)
            .where(where)  # type: ignore[arg-type]
            .values(values)
            .returning(self.__model__)
        )

        return await session.execute(query)

    async def many(
        self,
        session: AsyncSession,
        values: DictStrAny,
        where: Optional[Any] = None,
    ) -> Optional[Sequence[CRUDClassT]]:
        cursor = await self.query(session=session, values=values, where=where)

        return cursor.scalars().all() or None

    async def one(
        self, session: AsyncSession, values: DictStrAny, where: Optional[Any] = None
    ) -> Optional[CRUDClassT]:
        cursor = await self.query(session=session, values=values, where=where)

        return cast(CRUDClassT, cursor.scalar())
