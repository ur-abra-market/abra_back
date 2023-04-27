from typing import List, Optional

from fastapi import APIRouter
from fastapi.exceptions import HTTPException
from fastapi.param_functions import Body, Depends, Path, Query
from sqlalchemy import and_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload
from starlette import status

from core.app import crud
from core.depends import UserObjects, auth_required, get_session
from orm import SellerAddressModel, SellerModel, UserModel, UserNotificationModel
from schemas import (
    ApplicationResponse,
    BodySellerAddressRequest,
    BodySellerAddressUpdateRequest,
    BodyUserDataRequest,
    BodyUserNotificationRequest,
    SellerAddress,
    User,
)
from typing_ import RouteReturnT


async def seller_required(user: UserObjects = Depends(auth_required)) -> None:
    if not user.orm.seller:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Seller not found",
        )


router = APIRouter(dependencies=[Depends(seller_required)])


async def get_seller_info_core(session: AsyncSession, user_id: int) -> UserModel:
    return await crud.users.by.one(
        session=session,
        id=user_id,
        options=[
            joinedload(UserModel.seller).joinedload(SellerModel.addresses),
            joinedload(UserModel.seller).joinedload(SellerModel.image),
            joinedload(UserModel.notification),
        ],
    )


@router.get(
    path="/getSellerInfo/",
    summary="WORKS: returns dict with profile info, addresses, notifications, photo information",
    response_model=ApplicationResponse[User],
    status_code=status.HTTP_200_OK,
)
@router.get(
    path="/get_seller_info/",
    description="Moved to /sellers/getSellerInfo",
    deprecated=True,
    summary="WORKS: returns dict with profile info, addresses, notifications, photo information",
    response_model=ApplicationResponse[User],
    status_code=status.HTTP_308_PERMANENT_REDIRECT,
)
async def get_seller_info(
    user: UserObjects = Depends(auth_required), session: AsyncSession = Depends(get_session)
) -> RouteReturnT:
    return {
        "ok": True,
        "result": await get_seller_info_core(session=session, user_id=user.schema.id),
    }


@router.get(
    path="/getOrderStatus/",
    summary="Not working yet",
    response_model=ApplicationResponse[None],
    status_code=status.HTTP_200_OK,
)
@router.get(
    path="/get_order_status/",
    description="Moved to /sellers/getOrderStatus",
    deprecated=True,
    summary="Not working yet",
    response_model=ApplicationResponse[None],
    status_code=status.HTTP_308_PERMANENT_REDIRECT,
)
async def get_order_status() -> RouteReturnT:
    return {
        "ok": False,
        "detail": "Not worked yet",
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
@router.post(
    path="/send_seller_info/",
    description="Moved to /sellers/sendSellerInfo",
    deprecated=True,
    summary="WORKS: update seller data",
    response_model=ApplicationResponse[bool],
    status_code=status.HTTP_308_PERMANENT_REDIRECT,
)
async def send_seller_info(
    user_data_request: Optional[BodyUserDataRequest] = Body(None),
    seller_address_update_request: Optional[BodySellerAddressUpdateRequest] = Body(None),
    user_notifications_request: Optional[BodyUserNotificationRequest] = Body(None),
    user: UserObjects = Depends(auth_required),
    session: AsyncSession = Depends(get_session),
) -> RouteReturnT:
    await send_seller_info_core(
        session=session,
        user_id=user.schema.id,
        seller_id=user.schema.seller.id,
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
@router.post(
    path="/add_address/",
    description="Moved to /sellers/addAddress",
    deprecated=True,
    summary="WORKS: add a address for user",
    response_model=ApplicationResponse[SellerAddress],
    status_code=status.HTTP_308_PERMANENT_REDIRECT,
)
async def add_seller_address(
    request: BodySellerAddressRequest = Body(...),
    user: UserObjects = Depends(auth_required),
    session: AsyncSession = Depends(get_session),
) -> RouteReturnT:
    return {
        "ok": True,
        "result": await add_seller_address_core(
            session=session, seller_id=user.schema.seller.id, request=request
        ),
    }


async def update_address_core(
    session: AsyncSession,
    address_id: int,
    seller_id: int,
    request: BodySellerAddressUpdateRequest,
) -> SellerAddressModel:
    return await crud.sellers_addresses.update.one(
        session=session,
        values=request.dict(),
        where=and_(SellerAddressModel.id == address_id, SellerAddressModel.seller_id == seller_id),
    )


@router.patch(
    path="/updateAddress/",
    summary="WORKS: update the address for user",
    response_model=ApplicationResponse[SellerAddress],
    status_code=status.HTTP_200_OK,
)
@router.patch(
    path="/update_addresses/",
    description="Moved to /sellers/updateAddress",
    deprecated=True,
    summary="WORKS: update the address for user",
    response_model=ApplicationResponse[SellerAddress],
    status_code=status.HTTP_308_PERMANENT_REDIRECT,
)
async def update_address(
    address_id: int = Query(...),
    request: BodySellerAddressUpdateRequest = Body(...),
    user: UserObjects = Depends(auth_required),
    session: AsyncSession = Depends(get_session),
) -> RouteReturnT:
    return {
        "ok": True,
        "result": await update_address_core(
            session=session,
            address_id=address_id,
            seller_id=user.schema.seller.id,
            request=request,
        ),
    }


async def get_seller_addresses_core(
    session: AsyncSession, seller_id: int
) -> List[SellerAddressModel]:
    return await crud.sellers_addresses.by.many(session=session, seller_id=seller_id)


@router.get(
    path="/addresses/",
    summary="WORKS: gets a seller addresses",
    response_model=ApplicationResponse[List[SellerAddress]],
    status_code=status.HTTP_200_OK,
)
async def get_seller_addresses(
    user: UserObjects = Depends(auth_required),
    session: AsyncSession = Depends(get_session),
) -> RouteReturnT:
    return {
        "ok": True,
        "result": await get_seller_addresses_core(
            session=session,
            seller_id=user.schema.seller.id,
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
@router.delete(
    path="/remove_addresses/{address_id}/",
    description="Moved to /sellers/removeAddresses/{address_id}",
    deprecated=True,
    summary="WORKS: remove user address by id",
    response_model=ApplicationResponse[bool],
    status_code=status.HTTP_308_PERMANENT_REDIRECT,
)
async def remove_seller_address(
    address_id: int = Path(...),
    user: UserObjects = Depends(auth_required),
    session: AsyncSession = Depends(get_session),
) -> RouteReturnT:
    await remove_seller_address_core(
        session=session,
        address_id=address_id,
        seller_id=user.schema.seller.id,
    )

    return {
        "ok": True,
        "result": True,
    }
