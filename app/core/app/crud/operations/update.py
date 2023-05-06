from __future__ import annotations

from typing import Any, List, Optional, Union

from sqlalchemy import update
from sqlalchemy.sql.dml import ReturningUpdate

from typing_ import DictStrAny

from .base import CRUDClassT, CRUDOperation


class Update(CRUDOperation[CRUDClassT]):
    def query(
        self,
        values: Union[DictStrAny, List[DictStrAny]],
        where: Optional[Any] = None,
    ) -> ReturningUpdate[Any]:
        """
        Builds the query, for update.

        :param values: values to be inserted into model
        :param where: where conditions
        :return: constructed query
        """

        query = (
            update(self.__model__)
            .where(where)  # type: ignore[arg-type]
            .values(values)
            .returning(self.__model__)
        )

        return query  # noqa
