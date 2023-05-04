from typing import List, Optional

from fastapi import APIRouter
from fastapi.exceptions import HTTPException
from fastapi.param_functions import Body, Depends, Path, Query
from sqlalchemy import and_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload
from starlette import status

from core.app import crud
from core.depends import Authorization, DatabaseSession
from orm import (
    OrderModel,
    SellerAddressModel,
    SellerDeliveryModel,
    UserModel,
    UserNotificationModel,
)
from schemas import (
    ApplicationResponse,
    BodySellerAddressRequest,
    BodySellerAddressUpdateRequest,
    BodySellerDeliveryDataRequest,
    BodyUserDataRequest,
    BodyUserNotificationRequest,
    OrderStatus,
    SellerAddress,
    User,
)
from typing_ import RouteReturnT


async def seller_required(user: Authorization) -> None:
    if not user.seller:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Seller not found",
        )


router = APIRouter(dependencies=[Depends(seller_required)])


@router.get(
    path="/getSellerInfo/",
    deprecated=True,
    description="Moved to /login/current/",
    summary="WORKS: returns dict with profile info, addresses, notifications, photo information",
    response_model=ApplicationResponse[User],
    status_code=status.HTTP_308_PERMANENT_REDIRECT,
)
async def get_seller_info(user: Authorization) -> RouteReturnT:
    return {
        "ok": True,
        "result": user,
    }


@router.get(
    path="/getOrderStatus/",
    summary="WORKS: returns order status",
    response_model=ApplicationResponse[OrderStatus],
    status_code=status.HTTP_200_OK,
)
async def get_order_status(
    user: Authorization,
    session: DatabaseSession,
    order_id: int = Query(...),
) -> RouteReturnT:
    order = await crud.orders.get.one(
        session=session,
        where=[and_(OrderModel.id == order_id, OrderModel.seller_id == user.seller.id)],
        options=[joinedload(OrderModel.status)],
    )
    if not order:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Order not found")

    return {
        "ok": True,
        "result": order.status,
    }


async def send_seller_info_core(
    session: AsyncSession,
    user_id: int,
    seller_id: int,
    user_data_request: Optional[BodyUserDataRequest] = None,
    seller_address_update_request: Optional[BodySellerAddressUpdateRequest] = None,
    user_notifications_request: Optional[BodyUserNotificationRequest] = None,
) -> None:
    if user_data_request:
        await crud.users.update.one(
            session=session, values=user_data_request.dict(), where=UserModel.id == user_id
        )
    if seller_address_update_request:
        await crud.sellers_addresses.update.one(
            session=session,
            values=seller_address_update_request.dict(exclude={"address_id"}),
            where=and_(
                SellerAddressModel.id == seller_address_update_request.address_id,
                SellerAddressModel.seller_id == seller_id,
            ),
        )
    if user_notifications_request:
        await crud.users_notifications.update.one(
            session=session,
            values=user_notifications_request.dict(),
            where=UserNotificationModel.user_id == user_id,
        )


@router.post(
    path="/sendSellerInfo/",
    summary="WORKS: update seller data",
    response_model=ApplicationResponse[bool],
    status_code=status.HTTP_200_OK,
)
async def send_seller_info(
    user: Authorization,
    session: DatabaseSession,
    user_data_request: Optional[BodyUserDataRequest] = Body(None),
    seller_address_update_request: Optional[BodySellerAddressUpdateRequest] = Body(None),
    user_notifications_request: Optional[BodyUserNotificationRequest] = Body(None),
) -> RouteReturnT:
    await send_seller_info_core(
        session=session,
        user_id=user.id,
        seller_id=user.seller.id,
        user_data_request=user_data_request,
        seller_address_update_request=seller_address_update_request,
        user_notifications_request=user_notifications_request,
    )

    return {
        "ok": True,
        "result": True,
    }


async def add_seller_address_core(
    session: AsyncSession,
    seller_id: int,
    request: BodySellerAddressRequest,
) -> SellerAddressModel:
    return await crud.sellers_addresses.insert.one(
        session=session,
        values={
            SellerAddressModel.seller_id: seller_id,
            **request.dict(),
        },
    )


@router.post(
    path="/addAddress/",
    summary="WORKS: add a address for user",
    response_model=ApplicationResponse[SellerAddress],
    status_code=status.HTTP_201_CREATED,
)
async def add_seller_address(
    user: Authorization,
    session: DatabaseSession,
    request: BodySellerAddressRequest = Body(...),
) -> RouteReturnT:
    return {
        "ok": True,
        "result": await add_seller_address_core(
            session=session, seller_id=user.seller.id, request=request
        ),
    }


async def update_address_core(
    session: AsyncSession,
    seller_id: int,
    request: BodySellerAddressUpdateRequest,
) -> SellerAddressModel:
    return await crud.sellers_addresses.update.one(
        session=session,
        values=request.dict(exclude={"address_id"}),
        where=and_(
            SellerAddressModel.id == request.address_id,
            SellerAddressModel.seller_id == seller_id,
        ),
    )


@router.patch(
    path="/updateAddress/",
    summary="WORKS: update the address for user",
    response_model=ApplicationResponse[SellerAddress],
    status_code=status.HTTP_200_OK,
)
async def update_address(
    user: Authorization,
    session: DatabaseSession,
    request: BodySellerAddressUpdateRequest = Body(...),
) -> RouteReturnT:
    return {
        "ok": True,
        "result": await update_address_core(
            session=session,
            seller_id=user.seller.id,
            request=request,
        ),
    }


async def get_seller_addresses_core(
    session: AsyncSession, seller_id: int
) -> List[SellerAddressModel]:
    return await crud.sellers_addresses.get.many(
        session=session,
        where=[SellerAddressModel.seller_id == seller_id],
    )


@router.get(
    path="/addresses/",
    summary="WORKS: gets a seller addresses",
    response_model=ApplicationResponse[List[SellerAddress]],
    status_code=status.HTTP_200_OK,
)
async def get_seller_addresses(
    user: Authorization,
    session: DatabaseSession,
) -> RouteReturnT:
    return {
        "ok": True,
        "result": await get_seller_addresses_core(
            session=session,
            seller_id=user.seller.id,
        ),
    }


async def remove_seller_address_core(
    session: AsyncSession,
    address_id: int,
    seller_id: int,
) -> None:
    await crud.sellers_addresses.delete.one(
        session=session,
        where=and_(SellerAddressModel.id == address_id, SellerAddressModel.seller_id == seller_id),
    )


@router.delete(
    path="/removeAddress/{address_id}/",
    summary="WORKS: remove user address by id",
    response_model=ApplicationResponse[bool],
    status_code=status.HTTP_200_OK,
)
async def remove_seller_address(
    user: Authorization,
    session: DatabaseSession,
    address_id: int = Path(...),
) -> RouteReturnT:
    await remove_seller_address_core(
        session=session,
        address_id=address_id,
        seller_id=user.seller.id,
    )

    return {
        "ok": True,
        "result": True,
    }


async def seller_delivery_core(
    session: AsyncSession,
    request: BodySellerDeliveryDataRequest,
    seller_id: int,
) -> None:
    await crud.seller_delivery.insert.one(
        session=session,
        values={
            SellerDeliveryModel.seller_id: seller_id,
        }
        | request.dict(),
    )


@router.post(
    path="/delivery/",
    summary="WORKS: Delivery information (currency, country)",
    response_model=ApplicationResponse[bool],
    status_code=status.HTTP_201_CREATED,
)
async def delivery_information(
    user: Authorization,
    session: DatabaseSession,
    request: BodySellerDeliveryDataRequest = Body(...),
) -> RouteReturnT:
    await seller_delivery_core(
        session=session,
        seller_id=user.seller.id,
        request=request,
    )

    return {
        "ok": True,
        "result": True,
    }
