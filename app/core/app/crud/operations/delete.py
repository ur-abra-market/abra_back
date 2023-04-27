from __future__ import annotations

from typing import Any, Optional, Sequence, cast

from sqlalchemy import Result, delete
from sqlalchemy.ext.asyncio import AsyncSession

from .base import CRUDClassT, CrudOperation


class Delete(CrudOperation[CRUDClassT]):
    async def query(self, session: AsyncSession, where: Optional[Any] = None) -> Result[Any]:
        query = (
            delete(self.__model__).where(where).returning(self.__model__)  # type: ignore[arg-type]
        )

        return await session.execute(query)

    async def many(
        self, session: AsyncSession, where: Optional[Any] = None
    ) -> Optional[Sequence[CRUDClassT]]:
        cursor = await self.query(
            session=session,
            where=where,
        )

        return cursor.scalars().all() or None

    async def one(
        self,
        session: AsyncSession,
        where: Optional[Any] = None,
    ) -> Optional[CRUDClassT]:
        cursor = await self.query(session=session, where=where)

        return cast(CRUDClassT, cursor.scalar())
