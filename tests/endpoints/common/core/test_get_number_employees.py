from __future__ import annotations

from typing import List

from sqlalchemy.ext.asyncio import AsyncSession

from api.routers.common.info import get_employees_number_core


async def test_get_employees_number_core(session: AsyncSession) -> None:
    result = await get_employees_number_core(session=session)

    assert isinstance(result, List)
