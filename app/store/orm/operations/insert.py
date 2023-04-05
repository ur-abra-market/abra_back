from __future__ import annotations

from typing import TYPE_CHECKING, Any, Dict, Generic, List, Optional, TypeVar, Union

from sqlalchemy import Result
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import AsyncSession

from .base import BaseOperation

ClassT = TypeVar("ClassT")


class Insert(BaseOperation, Generic[ClassT]):
    if TYPE_CHECKING:
        model: ClassT

    async def insert_impl(
        self,
        session: AsyncSession,
        values: List[ClassT],
    ) -> Result[ClassT]:
        return await session.execute(insert(self.model).values(values).returning(self.model))

    async def insert_many(
        self, session: AsyncSession, values: List[Dict[str, Any]]
    ) -> List[ClassT]:
        cursor = await self.insert_impl(session=session, values=values)

        return cursor.scalars().all() or None

    async def insert_one(self, session: AsyncSession, values: Dict[str, Any]) -> Optional[ClassT]:
        cursor = await self.insert_impl(session=session, values=values)

        return cursor.scalar()
