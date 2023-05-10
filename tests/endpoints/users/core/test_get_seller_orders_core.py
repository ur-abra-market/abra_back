from __future__ import annotations

from typing import List

from sqlalchemy.ext.asyncio import AsyncSession

from api.routers.users import get_seller_orders_core


async def test_get_all_categories_core(session: AsyncSession) -> None:
    result = await get_seller_orders_core(seller_id=1, session=session)

    assert isinstance(result, List)
