from __future__ import annotations

from typing import List

from sqlalchemy.ext.asyncio import AsyncSession

from api.routers.sellers import get_seller_orders_core


async def test_get_seller_orders_core(session: AsyncSession, seller_id: int) -> None:
    result = await get_seller_orders_core(
        session=session,
        seller_id=seller_id,
        offset=0,
        limit=100,
    )

    assert isinstance(result, List)
