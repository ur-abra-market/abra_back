from __future__ import annotations

from typing import Any, Generic, Type

from .operations import CRUDClassT, Delete, Get, Insert, Update


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
