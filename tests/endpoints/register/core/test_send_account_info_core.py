from __future__ import annotations

from sqlalchemy.ext.asyncio import AsyncSession

from api.routers.register import send_account_info_core
from orm import UserModel
from schemas import BodyUserDataRequest, Seller
from typing_ import DictStrAny


async def test_send_account_info_core(
    session: AsyncSession, add_account_info_request: DictStrAny, pure_seller: UserModel
) -> None:
    seller = Seller.from_orm(pure_seller)
    body_user_data_request = BodyUserDataRequest.parse_obj(add_account_info_request)

    await send_account_info_core(
        session=session,
        request=body_user_data_request,
        user_id=seller.id,
    )

    assert seller.dict().items() <= body_user_data_request.dict().items()
