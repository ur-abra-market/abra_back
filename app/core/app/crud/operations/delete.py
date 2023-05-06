from __future__ import annotations

from typing import Any, Optional, Sequence, cast

from sqlalchemy import delete
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql.dml import ReturningDelete

from .base import CRUDClassT, CrudOperation


class Delete(CrudOperation[CRUDClassT]):
    def query(
        self,
        where: Optional[Any] = None,
        returning: Optional[Sequence[Any]] = None,
    ) -> ReturningDelete[Any]:
        """
        Builds the query, for delete.

        :param where: where conditions
        :param returning: what should come back from the delete
        :return: constructed query
        """

        returning = self.transform((self.__model__, returning))  # type: ignore[arg-type]

        query = delete(self.__model__).where(where).returning(*returning)

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
