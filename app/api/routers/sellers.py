from typing import List

from corecrud import Options, Returning, Values, Where
from fastapi import APIRouter
from fastapi.exceptions import HTTPException
from fastapi.param_functions import Depends
from sqlalchemy import and_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload
from starlette import status

from core.app import crud
from core.depends import DatabaseSession, SellerAuthorization, seller
from orm import OrderModel, SellerAddressModel, SellerModel
from schemas import (
    ApplicationResponse,
    BodySellerAddressRequest,
    BodySellerAddressUpdateRequest,
    OrderStatus,
    SellerAddress,
)
from typing_ import RouteReturnT
from utils.fastapi import Body, Path, Query

router = APIRouter(dependencies=[Depends(seller)])


@router.get(
    path="/getOrderStatus/",
    summary="WORKS: returns order status",
    response_model=ApplicationResponse[OrderStatus],
    status_code=status.HTTP_200_OK,
)
async def get_order_status(
    user: SellerAuthorization,
    session: DatabaseSession,
    order_id: int = Query(alias="orderId"),
) -> RouteReturnT:
    order = await crud.orders.select.one(
        Where(and_(OrderModel.id == order_id, OrderModel.seller_id == user.seller.id)),
        Options(joinedload(OrderModel.status)),
        session=session,
    )
    if not order:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Order not found")

    return {
        "ok": True,
        "result": order.status,
    }


async def has_main_address_core(
    session: AsyncSession,
    seller_id: int,
    has_main_address: bool,
    is_main: bool,
) -> None:
    if has_main_address:
        await crud.sellers_addresses.update.one(
            Values(
                {
                    SellerAddressModel.is_main: not is_main,
                },
            ),
            Where(SellerAddressModel.seller_id == seller_id, SellerAddressModel.is_main.is_(True)),
            Returning(SellerAddressModel.id),
            session=session,
        )

    await crud.sellers.update.one(
        Values({SellerModel.has_main_address: is_main}),
        Where(SellerModel.id == seller_id),
        Returning(SellerModel.id),
        session=session,
    )


async def add_seller_address_core(
    session: AsyncSession,
    seller_id: int,
    has_main_address: bool,
    request: BodySellerAddressRequest,
) -> SellerAddressModel:
    await has_main_address_core(
        session=session,
        seller_id=seller_id,
        has_main_address=has_main_address,
        is_main=request.is_main,
    )

    return await crud.sellers_addresses.insert.one(
        Values(
            {
                SellerAddressModel.seller_id: seller_id,
            }
            | request.dict(),
        ),
        Returning(SellerAddressModel),
        session=session,
    )


@router.post(
    path="/addAddress/",
    summary="WORKS: add a address for user",
    response_model=ApplicationResponse[SellerAddress],
    status_code=status.HTTP_201_CREATED,
)
async def add_seller_address(
    user: SellerAuthorization,
    session: DatabaseSession,
    request: BodySellerAddressRequest = Body(...),
) -> RouteReturnT:
    return {
        "ok": True,
        "result": await add_seller_address_core(
            session=session,
            seller_id=user.seller.id,
            has_main_address=user.seller.has_main_address,
            request=request,
        ),
    }


async def update_address_core(
    session: AsyncSession,
    seller_id: int,
    has_main_address: bool,
    request: BodySellerAddressUpdateRequest,
) -> SellerAddressModel:
    await has_main_address_core(
        session=session,
        seller_id=seller_id,
        has_main_address=has_main_address,
        is_main=request.is_main,
    )

    return await crud.sellers_addresses.update.one(
        Values(request.dict(exclude={"address_id"})),
        Where(
            and_(
                SellerAddressModel.id == request.address_id,
                SellerAddressModel.seller_id == seller_id,
            )
        ),
        Returning(SellerAddressModel),
        session=session,
    )


@router.patch(
    path="/updateAddress/",
    summary="WORKS: update the address for user",
    response_model=ApplicationResponse[SellerAddress],
    status_code=status.HTTP_200_OK,
)
async def update_address(
    user: SellerAuthorization,
    session: DatabaseSession,
    request: BodySellerAddressUpdateRequest = Body(...),
) -> RouteReturnT:
    return {
        "ok": True,
        "result": await update_address_core(
            session=session,
            seller_id=user.seller.id,
            has_main_address=user.seller.has_main_address,
            request=request,
        ),
    }


@router.get(
    path="/addresses/",
    summary="WORKS: gets a seller addresses",
    response_model=ApplicationResponse[List[SellerAddress]],
    status_code=status.HTTP_200_OK,
)
async def get_seller_addresses(user: SellerAuthorization) -> RouteReturnT:
    return {
        "ok": True,
        "result": user.seller.addresses,
    }


async def remove_seller_address_core(
    session: AsyncSession,
    address_id: int,
    seller_id: int,
) -> None:
    await crud.sellers_addresses.delete.one(
        Where(
            and_(SellerAddressModel.id == address_id, SellerAddressModel.seller_id == seller_id)
        ),
        Returning(SellerAddressModel.id),
        session=session,
    )


@router.delete(
    path="/removeAddress/{address_id}/",
    summary="WORKS: remove user address by id",
    response_model=ApplicationResponse[bool],
    status_code=status.HTTP_200_OK,
)
async def remove_seller_address(
    user: SellerAuthorization,
    session: DatabaseSession,
    address_id: int = Path(alias="addressId"),
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
