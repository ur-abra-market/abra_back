from __future__ import annotations

from typing import List

from sqlalchemy.ext.asyncio import AsyncSession

from api.routers.users import get_seller_orders_core


async def test_get_all_categories_core(
    session: AsyncSession,
    seller_id: int,
) -> None:
    result = await get_seller_orders_core(seller_id=seller_id, session=session)

    assert isinstance(result, List)
