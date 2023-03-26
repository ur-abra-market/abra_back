from __future__ import annotations

from typing import TYPE_CHECKING, Any, Dict, Generic, List, Optional, Sequence, TypeVar, Union

from sqlalchemy import Result, update
from sqlalchemy.ext.asyncio import AsyncSession

from .base import BaseOperation

ClassT = TypeVar("ClassT")


class Update(BaseOperation, Generic[ClassT]):
    if TYPE_CHECKING:
        model: ClassT

    async def update_impl(
        self,
        session: AsyncSession,
        values: Union[Dict[str, Any], List[Dict[str, Any]]],
        where: Optional[Any] = None,
    ) -> Result[ClassT]:
        return await session.execute(
            update(self.model).where(where).values(values).returning(self.model)
        )

    async def update_many(
        self,
        session: AsyncSession,
        values: List[Dict[str, Any]],
        where: Optional[Any] = None,
    ) -> Optional[List[ClassT]]:
        cursor = await self.update_impl(session=session, values=values, where=where)

        return cursor.scalars().all() or None

    async def update_one(
        self, session: AsyncSession, values: Dict[str, Any], where: Optional[Any] = None
    ) -> Optional[ClassT]:
        cursor = await self.update_impl(session=session, values=values, where=where)

        return cursor.scalar()
