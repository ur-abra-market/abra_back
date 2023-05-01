from __future__ import annotations

from typing import Any, Optional, Sequence, cast

from sqlalchemy import delete
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql.dml import ReturningDelete

from .base import CRUDClassT, CrudOperation


class Delete(CrudOperation[CRUDClassT]):
    def query(self, where: Optional[Any] = None) -> ReturningDelete[Any]:
        query = (
            delete(self.__model__).where(where).returning(self.__model__)  # type: ignore[arg-type]
        )

        return query  # noqa

    async def many(
        self, session: AsyncSession, where: Optional[Any] = None
    ) -> Sequence[CRUDClassT]:
        cursor = await self.execute(session, where=where)

        return cast(Sequence[CRUDClassT], cursor.scalars().all())

    async def one(
        self, session: AsyncSession, where: Optional[Any] = None
    ) -> Optional[CRUDClassT]:
        cursor = await self.execute(session, where=where)

        return cast(CRUDClassT, cursor.scalar())
