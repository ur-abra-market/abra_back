from __future__ import annotations

from typing import TYPE_CHECKING

from app.store.orm.base import ORMAccessor
from app.orm import CategoryModel

if TYPE_CHECKING:
    from app.store import Store


class ORM:
    def __init__(self) -> None:
        self.categories: ORMAccessor[CategoryModel] = ORMAccessor(CategoryModel)
