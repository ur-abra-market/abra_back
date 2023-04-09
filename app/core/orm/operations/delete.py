from __future__ import annotations

from typing import Any, Generic, Optional, Sequence, TypeVar, cast

from sqlalchemy import Result, delete
from sqlalchemy.ext.asyncio import AsyncSession

from .base import BaseOperation

ClassT = TypeVar("ClassT")


class Delete(BaseOperation[ClassT], Generic[ClassT]):
    async def delete_impl(self, session: AsyncSession, where: Optional[Any] = None) -> Result[Any]:
        query = delete(self.__model__).where(where).returning(self.__model__)
        return await session.execute(query)

    async def delete_many(
        self, session: AsyncSession, where: Optional[Any] = None
    ) -> Optional[Sequence[ClassT]]:
        cursor = await self.delete_impl(
            session=session,
            where=where,
        )

        return cursor.scalars().all() or None

    async def delete_one(
        self,
        session: AsyncSession,
        where: Optional[Any] = None,
    ) -> Optional[ClassT]:
        cursor = await self.delete_impl(session=session, where=where)

        return cast(ClassT, cursor.scalar())
