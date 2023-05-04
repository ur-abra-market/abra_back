from __future__ import annotations

from sqlalchemy.ext.asyncio import AsyncSession

from api.routers.sellers import seller_delivery_core
from core.app import crud
from orm import SellerDeliveryModel
from schemas import BodySellerDeliveryDataRequest
from typing_ import DictStrAny


async def test_seller_delivery_core(
    session: AsyncSession, add_seller_delivery_request: DictStrAny, seller_id: int
) -> None:
    await seller_delivery_core(
        session=session,
        request=BodySellerDeliveryDataRequest.parse_obj(add_seller_delivery_request),
        seller_id=seller_id,
    )

    result = await crud.seller_delivery.get.one(
        session=session, where=[SellerDeliveryModel.seller_id == seller_id]
    )
    assert result
