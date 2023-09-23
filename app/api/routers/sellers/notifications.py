from typing import Optional

from corecrud import Returning, Values, Where
from fastapi import APIRouter
from fastapi.param_functions import Body
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from core.app import crud
from core.depends import DatabaseSession, SellerAuthorization
from orm import SellerNotificationsModel
from schemas import ApplicationResponse, SellerNotifications
from schemas.uploads import SellerNotificationsUpdateUpload
from typing_ import RouteReturnT

router = APIRouter()


async def update_notifications_core(
    session: AsyncSession,
    seller_id: int,
    notification_data_request: Optional[SellerNotificationsUpdateUpload],
) -> None:
    if notification_data_request:
        await crud.sellers_notifications.update.one(
            Values(notification_data_request.dict()),
            Where(SellerNotificationsModel.seller_id == seller_id),
            Returning(SellerNotificationsModel.id),
            session=session,
        )


@router.post(
    "/update",
    summary="WORKS: update seller notifications",
    response_model=ApplicationResponse[bool],
    status_code=status.HTTP_200_OK,
)
async def update_notifications(
    user: SellerAuthorization,
    session: DatabaseSession,
    notification_data_request: Optional[SellerNotificationsUpdateUpload] = Body(None),
) -> RouteReturnT:
    await update_notifications_core(
        session=session,
        seller_id=user.seller.id,
        notification_data_request=notification_data_request,
    )

    return {
        "ok": True,
        "result": True,
    }


async def get_notifications_core(
    session: AsyncSession,
    seller_id: int,
) -> SellerNotificationsModel:
    return await crud.sellers_notifications.select.one(
        Where(SellerNotificationsModel.seller_id == seller_id),
        session=session,
    )


@router.get(
    "/",
    summary="WORKS: get seller notifications",
    response_model=ApplicationResponse[SellerNotifications],
    status_code=status.HTTP_200_OK,
)
async def get_notifications(
    user: SellerAuthorization,
    session: DatabaseSession,
) -> RouteReturnT:
    return {
        "ok": True,
        "result": await get_notifications_core(session=session, seller_id=user.seller.id),
    }
