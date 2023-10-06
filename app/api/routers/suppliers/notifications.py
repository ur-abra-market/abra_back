from typing import Optional

from corecrud import Returning, Values, Where
from fastapi import APIRouter
from fastapi.param_functions import Body
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from core.app import crud
from core.depends import DatabaseSession, SupplierAuthorization
from orm import SupplierNotificationsModel
from schemas import ApplicationResponse, SupplierNotifications
from schemas.uploads import SupplierNotificationsUpdateUpload
from typing_ import RouteReturnT

router = APIRouter()


async def update_notifications_core(
    session: AsyncSession,
    supplier_id: int,
    notification_data_request: Optional[SupplierNotificationsUpdateUpload],
) -> None:
    if notification_data_request:
        await crud.suppliers_notifications.update.one(
            Values(notification_data_request.dict()),
            Where(SupplierNotificationsModel.supplier_id == supplier_id),
            Returning(SupplierNotificationsModel.id),
            session=session,
        )


@router.post(
    path="/update",
    summary="WORKS: update notifications for supplier",
    response_model=ApplicationResponse[bool],
    status_code=status.HTTP_200_OK,
)
async def update_notifications(
    user: SupplierAuthorization,
    session: DatabaseSession,
    notification_data_request: Optional[SupplierNotificationsUpdateUpload] = Body(None),
) -> RouteReturnT:
    await update_notifications_core(
        session=session,
        supplier_id=user.supplier.id,
        notification_data_request=notification_data_request,
    )

    return {
        "ok": True,
        "result": True,
    }


async def get_notifications_core(
    session: AsyncSession,
    supplier_id: int,
) -> SupplierNotificationsModel:
    return await crud.suppliers_notifications.select.one(
        Where(SupplierNotificationsModel.supplier_id == supplier_id),
        session=session,
    )


@router.get(
    "",
    summary="WORKS: get supplier notifications",
    response_model=ApplicationResponse[SupplierNotifications],
    status_code=status.HTTP_200_OK,
)
async def get_notifications(
    user: SupplierAuthorization,
    session: DatabaseSession,
) -> RouteReturnT:
    return {
        "ok": True,
        "result": await get_notifications_core(session=session, supplier_id=user.supplier.id),
    }
