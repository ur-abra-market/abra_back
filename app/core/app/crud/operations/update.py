from __future__ import annotations

from typing import Any, List, Optional, Sequence, Union, cast

from sqlalchemy import update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql.dml import ReturningUpdate

from typing_ import DictStrAny

from .base import CRUDClassT, CrudOperation


class Update(CrudOperation[CRUDClassT]):
    def query(
        self, values: Union[DictStrAny, List[DictStrAny]], where: Optional[Any] = None
    ) -> ReturningUpdate[Any]:
        query = (
            update(self.__model__)
            .where(where)  # type: ignore[arg-type]
            .values(values)
            .returning(self.__model__)
        )

        return query  # noqa

    async def many(
        self, session: AsyncSession, values: DictStrAny, where: Optional[Any] = None
    ) -> Sequence[CRUDClassT]:
        cursor = await self.execute(session, values=values, where=where)

        return cast(Sequence[CRUDClassT], cursor.scalars().all())

    async def one(
        self, session: AsyncSession, values: DictStrAny, where: Optional[Any] = None
    ) -> Optional[CRUDClassT]:
        cursor = await self.execute(session, values=values, where=where)

        return cast(CRUDClassT, cursor.scalar())
