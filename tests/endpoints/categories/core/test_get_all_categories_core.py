from __future__ import annotations

from typing import List

from sqlalchemy.ext.asyncio import AsyncSession

from api.routers.categories.base import get_all_categories_core


async def test_get_all_categories_core(session: AsyncSession) -> None:
    result = await get_all_categories_core(session=session)

    assert isinstance(result, List)
