from __future__ import annotations

from typing import Any, Dict

from sqlalchemy.ext.asyncio import AsyncSession

from core.app import crud
from api.routers.sellers import seller_delivery_core
from orm import SellerDeliveryModel
from schemas import BodySellerDeliveryDataRequest

async def test_seller_delivery_core(
        session: AsyncSession,
        add_seller_delivery_request: Dict[str, Any],
        seller_id: int
) -> None:
    await seller_delivery_core(
        session=session,
        request=BodySellerDeliveryDataRequest.parse_obj(add_seller_delivery_request),
        seller_id=seller_id,
    )

    result = await crud.seller_delivery.get.one(session=session, where=[SellerDeliveryModel.seller_id == seller_id])
    assert result

