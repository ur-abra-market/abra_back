from __future__ import annotations

import abc
from typing import Any, Generic, Optional, Sequence, Type

from sqlalchemy.ext.asyncio import AsyncSession

from .operations import CRUDClassT, CRUDOperation, Delete, Get, Insert, Update


class _CRUDOperationMappings(CRUDOperation[CRUDClassT], abc.ABC):
    async def one(
        self,
        *args: Any,
        session: AsyncSession,
        **kwargs: Any,
    ) -> Optional[Any]:
        cursor = await self.execute(session, *args, **kwargs)

        return await cursor.mappings().one_or_none()

    async def many(
        self,
        *args: Any,
        session: AsyncSession,
        **kwargs: Any,
    ) -> Sequence[Any]:
        cursor = await self.execute(session, *args, **kwargs)

        return await cursor.mappings().all()

    async def many_unique(
        self,
        *args: Any,
        session: AsyncSession,
        **kwargs: Any,
    ) -> Sequence[Any]:
        cursor = await self.execute(session, *args, **kwargs)

        return await cursor.unique().mappings().all()


class DeleteMappings(_CRUDOperationMappings[CRUDClassT], Delete[CRUDClassT]):
    ...


class GetMappings(_CRUDOperationMappings[CRUDClassT], Get[CRUDClassT]):
    ...


class InsertMappings(_CRUDOperationMappings[CRUDClassT], Insert[CRUDClassT]):
    ...


class UpdateMappings(_CRUDOperationMappings[CRUDClassT], Update[CRUDClassT]):
    ...


class CRUD(Generic[CRUDClassT]):
    def __init__(
        self,
        model: Type[Any] = None,  # type: ignore[assignment]
        *,
        get: Type[Get[CRUDClassT]] = Get,
        insert: Type[Insert[CRUDClassT]] = Insert,
        update: Type[Update[CRUDClassT]] = Update,
        delete: Type[Delete[CRUDClassT]] = Delete,
    ) -> None:
        self.get = get(model=model)
        self.insert = insert(model=model)
        self.update = update(model=model)
        self.delete = delete(model=model)
