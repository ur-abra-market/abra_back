# mypy: disable-error-code="attr-defined"

from __future__ import annotations

from typing import Any, List, Optional, Sequence, Union, cast

from sqlalchemy import Result
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import AsyncSession

from typing_ import DictStrAny

from .base import CRUDClassT, CrudOperation


class Insert(CrudOperation[CRUDClassT]):
    async def query(
        self,
        session: AsyncSession,
        values: Union[DictStrAny, List[DictStrAny]],
    ) -> Result[Any]:
        query = insert(self.__model__).values(values).returning(self.__model__)

        return await session.execute(query)

    async def many(
        self, session: AsyncSession, values: List[DictStrAny]
    ) -> Optional[Sequence[CRUDClassT]]:
        cursor = await self.query(session=session, values=values)

        return cursor.scalars().all() or None

    async def one(self, session: AsyncSession, values: DictStrAny) -> Optional[CRUDClassT]:
        cursor = await self.query(session=session, values=values)

        return cast(CRUDClassT, cursor.scalar())
