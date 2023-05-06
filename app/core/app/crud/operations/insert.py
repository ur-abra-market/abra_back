from __future__ import annotations

from typing import Any, List, Union

from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.sql.dml import ReturningInsert

from typing_ import DictStrAny

from .base import CRUDClassT, CRUDOperation


class Insert(CRUDOperation[CRUDClassT]):
    def query(self, values: Union[DictStrAny, List[DictStrAny]]) -> ReturningInsert[Any]:
        """
        Builds the query, for insert.

        :param values: values to be inserted into model
        :return: constructed query
        """

        query = insert(self.__model__).values(values).returning(self.__model__)

        return query  # noqa
