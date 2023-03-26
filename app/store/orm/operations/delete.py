from __future__ import annotations

from typing import TYPE_CHECKING, Any, Generic, List, Optional, TypeVar

from sqlalchemy import Result, delete
from sqlalchemy.ext.asyncio import AsyncSession

from .base import BaseOperation

ClassT = TypeVar("ClassT")


class Delete(BaseOperation, Generic[ClassT]):
    if TYPE_CHECKING:
        model: ClassT

    async def delete_impl(
        self, session: AsyncSession, where: Optional[Any] = None
    ) -> Result[ClassT]:
        return await session.execute(delete(self.model).where(where).returning(self.model))

    async def delete_many(
        self, session: AsyncSession, where: Optional[Any] = None
    ) -> Optional[List[ClassT]]:
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

        return cursor.scalar()
