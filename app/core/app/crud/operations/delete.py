from __future__ import annotations

from typing import Any, Optional

from sqlalchemy import delete
from sqlalchemy.sql.dml import ReturningDelete

from .base import CRUDClassT, CRUDOperation


class Delete(CRUDOperation[CRUDClassT]):
    def query(self, where: Optional[Any] = None) -> ReturningDelete[Any]:
        """
        Builds the query, for delete.

        :param where: where conditions
        :return: constructed query
        """

        query = delete(self.__model__).where(where).returning(self.__model__)

        return query  # noqa
