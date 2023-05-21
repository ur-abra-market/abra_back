from typing import List

from corecrud import Options, Returning, Values, Where
from fastapi import APIRouter
from fastapi.exceptions import HTTPException
from fastapi.param_functions import Body, Depends, Path, Query
from sqlalchemy import and_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload
from starlette import status

from core.app import crud
from core.depends import DatabaseSession, SellerAuthorization, seller
from orm import CountryModel, OrderModel, SellerAddressModel
from schemas import (
    ApplicationResponse,
    BodySellerAddressRequest,
    BodySellerAddressUpdateRequest,
    OrderStatus,
    SellerAddress,
)
from typing_ import RouteReturnT

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
    order_id: int = Query(...),
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


async def add_seller_address_core(
    session: AsyncSession,
    seller_id: int,
    country_id: int,
    request: BodySellerAddressRequest,
) -> SellerAddressModel:
    return await crud.sellers_addresses.insert.one(
        Values(
            {
                SellerAddressModel.seller_id: seller_id,
                SellerAddressModel.country_id: country_id,
            }
            | request.dict(exclude={"country_code"})
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
    country = await crud.country.select.one(
        Where(CountryModel.country_code == request.country_code),
        session=session,
    )

    return {
        "ok": True,
        "result": await add_seller_address_core(
            session=session, seller_id=user.seller.id, country_id=country.id, request=request
        ),
    }


async def update_address_core(
    session: AsyncSession,
    seller_id: int,
    country_id: int,
    request: BodySellerAddressUpdateRequest,
) -> SellerAddressModel:
    return await crud.sellers_addresses.update.one(
        Values(request.dict(exclude={"address_id"})),
        Where(
            and_(
                SellerAddressModel.id == request.address_id,
                SellerAddressModel.seller_id == seller_id,
                SellerAddressModel.country_id == country_id,
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
