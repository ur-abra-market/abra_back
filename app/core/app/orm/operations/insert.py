# mypy: disable-error-code="attr-defined"

from __future__ import annotations

from typing import Any, Dict, Generic, List, Optional, Sequence, TypeVar, Union, cast

from sqlalchemy import Result
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import AsyncSession

from .base import BaseOperation

ClassT = TypeVar("ClassT")


class Insert(BaseOperation[ClassT], Generic[ClassT]):
    async def insert_impl(
        self,
        session: AsyncSession,
        values: Union[Dict[str, Any], List[Dict[str, Any]]],
    ) -> Result[Any]:
        query = (
            insert(self.__model__)
            .values(values)
            .on_conflict_do_update(
                index_elements=[self.__model__.id],
                set_={
                    self.__model__.id: self.__model__.id - 1,
                },
            )
            .returning(self.__model__)
        )
        return await session.execute(query)

    async def insert_many(
        self, session: AsyncSession, values: List[Dict[str, Any]]
    ) -> Optional[Sequence[ClassT]]:
        cursor = await self.insert_impl(session=session, values=values)

        return cursor.scalars().all() or None

    async def insert_one(self, session: AsyncSession, values: Dict[str, Any]) -> Optional[ClassT]:
        cursor = await self.insert_impl(session=session, values=values)

        return cast(ClassT, cursor.scalar())
