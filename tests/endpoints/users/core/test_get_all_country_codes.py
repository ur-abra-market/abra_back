from __future__ import annotations

from typing import List

from sqlalchemy.ext.asyncio import AsyncSession

from api.routers.users import get_all_country_codes_core


async def test_get_all_country_codes_core(session: AsyncSession) -> None:
    result = await get_all_country_codes_core(session=session)

    assert isinstance(result, List)
