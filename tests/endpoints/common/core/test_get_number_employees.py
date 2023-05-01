from __future__ import annotations

from typing import List

from sqlalchemy.ext.asyncio import AsyncSession

from api.routers.common import get_number_employees_core


async def test_get_number_employees_core(session: AsyncSession) -> None:
    result = await get_number_employees_core(session=session)

    assert isinstance(result, List)
