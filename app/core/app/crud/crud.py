from __future__ import annotations

from typing import Generic, Type

from .operations import AliasCRUDClassT, By, CRUDClassT, Delete, Get, Insert, Update


class CRUD(Generic[CRUDClassT]):
    def __init__(
        self,
        model: AliasCRUDClassT = None,  # type: ignore[assignment]
        *,
        get: Type[Get[AliasCRUDClassT]] = Get,
        by: Type[By[AliasCRUDClassT]] = By,
        insert: Type[Insert[AliasCRUDClassT]] = Insert,
        update: Type[Update[AliasCRUDClassT]] = Update,
        delete: Type[Delete[AliasCRUDClassT]] = Delete,
    ) -> None:
        self.get = get(model=model)
        self.by = by(model=model)
        self.insert = insert(model=model)
        self.update = update(model=model)
        self.delete = delete(model=model)
