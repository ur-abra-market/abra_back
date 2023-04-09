# mypy: disable-error-code="arg-type,return-value"
from typing import List, Optional

from fastapi import APIRouter
from fastapi.exceptions import HTTPException
from fastapi.param_functions import Body, Depends, Path, Query
from sqlalchemy import and_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload
from starlette import status

from core.depends import UserObjects, auth_required, get_session
from core.orm import orm
from orm import UserAddressModel, UserModel, UserNotificationModel
from schemas import (
    ApplicationResponse,
    BodyUserAddressRequest,
    BodyUserAddressUpdateRequest,
    BodyUserDataRequest,
    BodyUserNotificationRequest,
    QueryPaginationRequest,
    User,
    UserAddress,
)


async def seller_required(user: UserObjects = Depends(auth_required)) -> None:
    if not user.orm.seller:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Seller not found",
        )


router = APIRouter(dependencies=[Depends(seller_required)])


async def get_seller_info_core(session: AsyncSession, user_id: int) -> UserModel:
    return await orm.users.get_one_by(
        session=session,
        id=user_id,
        options=[
            joinedload(UserModel.addresses),
            joinedload(UserModel.notification),
            joinedload(UserModel.image),
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
) -> ApplicationResponse[User]:
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
async def get_order_status() -> ApplicationResponse[None]:
    return {
        "ok": False,
        "detail": "Not worked yet",
    }


async def send_seller_info_core(
    session: AsyncSession,
    user_id: int,
    user_data_request: Optional[BodyUserDataRequest] = None,
    user_address_update_request: Optional[BodyUserAddressUpdateRequest] = None,
    user_notifications_request: Optional[BodyUserNotificationRequest] = None,
) -> None:
    if user_data_request:
        await orm.users.update_one(
            session=session, values=user_data_request.dict(), where=UserModel.id == user_id
        )
    if user_address_update_request:
        await orm.users_addresses.update_one(
            session=session,
            values=user_address_update_request.dict(exclude={"address_id"}),
            where=and_(
                UserAddressModel.id == user_address_update_request.address_id,
                UserAddressModel.user_id == user_id,
            ),
        )
    if user_notifications_request:
        await orm.users_notifications.update_one(
            session=session,
            values=user_notifications_request.dict(),
            where=UserNotificationModel.user_id == user_id,
        )


@router.post(
    path="/sendSellerInfo/",
    summary="WORKS: update seller data, full address is required, notifications - 1 route for all notifications",
    response_model=ApplicationResponse[bool],
    status_code=status.HTTP_200_OK,
)
@router.post(
    path="/send_seller_info/",
    description="Moved to /sellers/sendSellerInfo",
    deprecated=True,
    summary="WORKS: update seller data, full address is required, notifications - 1 route for all notifications",
    response_model=ApplicationResponse[bool],
    status_code=status.HTTP_308_PERMANENT_REDIRECT,
)
async def send_seller_info(
    user_data_request: Optional[BodyUserDataRequest] = Body(None),
    user_address_update_request: Optional[BodyUserAddressUpdateRequest] = Body(None),
    user_notifications_request: Optional[BodyUserNotificationRequest] = Body(None),
    user: UserObjects = Depends(auth_required),
    session: AsyncSession = Depends(get_session),
) -> ApplicationResponse[bool]:
    await send_seller_info_core(
        session=session,
        user_id=user.schema.id,
        user_data_request=user_data_request,
        user_address_update_request=user_address_update_request,
        user_notifications_request=user_notifications_request,
    )

    return {
        "ok": True,
        "result": True,
    }


async def add_seller_address_core(
    session: AsyncSession,
    user_id: int,
    request: BodyUserAddressRequest,
) -> UserAddressModel:
    return await orm.users_addresses.insert_one(
        session=session,
        values={
            UserAddressModel.user_id: user_id,
            **request.dict(),
        },
    )


@router.post(
    path="/addAddress/",
    summary="WORKS: add a address for user",
    response_model=ApplicationResponse[UserAddress],
    status_code=status.HTTP_201_CREATED,
)
@router.post(
    path="/add_address/",
    description="Moved to /sellers/addAddress",
    deprecated=True,
    summary="WORKS: add a address for user",
    response_model=ApplicationResponse[UserAddress],
    status_code=status.HTTP_308_PERMANENT_REDIRECT,
)
async def add_seller_address(
    request: BodyUserAddressRequest = Body(...),
    user: UserObjects = Depends(auth_required),
    session: AsyncSession = Depends(get_session),
) -> ApplicationResponse[UserAddress]:
    return {
        "ok": True,
        "result": await add_seller_address_core(
            session=session, user_id=user.schema.id, request=request
        ),
    }


async def update_address_core(
    session: AsyncSession,
    address_id: int,
    user_id: int,
    request: BodyUserAddressRequest,
) -> UserAddressModel:
    return await orm.users_addresses.update_one(
        session=session,
        values=request.dict(),
        where=and_(UserAddressModel.id == address_id, UserAddressModel.user_id == user_id),
    )


@router.patch(
    path="/updateAddress/",
    summary="WORKS: update the address for user",
    response_model=ApplicationResponse[UserAddress],
    status_code=status.HTTP_200_OK,
)
@router.patch(
    path="/update_addresses/",
    description="Moved to /sellers/updateAddress",
    deprecated=True,
    summary="WORKS: update the address for user",
    response_model=ApplicationResponse[UserAddress],
    status_code=status.HTTP_308_PERMANENT_REDIRECT,
)
async def update_address(
    address_id: int = Query(...),
    request: BodyUserAddressRequest = Body(...),
    user: UserObjects = Depends(auth_required),
    session: AsyncSession = Depends(get_session),
) -> ApplicationResponse[UserAddress]:
    return {
        "ok": True,
        "result": await update_address_core(
            session=session,
            address_id=address_id,
            user_id=user.schema.id,
            request=request,
        ),
    }


async def get_seller_addresses_core(
    session: AsyncSession,
    user_id: int,
    offset: int,
    limit: int,
) -> List[UserAddressModel]:
    return await orm.users_addresses.get_many_by(
        session=session,
        user_id=user_id,
        offset=offset,
        limit=limit,
    )


@router.get(
    path="/addresses/",
    summary="WORKS: gets a seller addresses",
    response_model=ApplicationResponse[List[UserAddress]],
    status_code=status.HTTP_201_CREATED,
)
async def get_seller_addresses(
    pagination: QueryPaginationRequest = Depends(),
    user: UserObjects = Depends(auth_required),
    session: AsyncSession = Depends(get_session),
) -> ApplicationResponse[List[UserAddress]]:
    return {
        "ok": True,
        "result": await get_seller_addresses_core(
            session=session,
            user_id=user.schema.id,
            offset=pagination.offset,
            limit=pagination.limit,
        ),
    }


async def remove_seller_address_core(
    session: AsyncSession,
    address_id: int,
    user_id: int,
) -> None:
    await orm.users_addresses.delete_one(
        session=session,
        where=and_(UserAddressModel.user_id == user_id, UserAddressModel.id == address_id),
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
) -> ApplicationResponse[bool]:
    await remove_seller_address_core(
        session=session,
        address_id=address_id,
        user_id=user.schema.id,
    )

    return {
        "ok": True,
        "result": True,
    }
