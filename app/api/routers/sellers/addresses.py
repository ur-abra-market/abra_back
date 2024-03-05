from typing import List

from corecrud import Options, Returning, Values, Where
from fastapi import APIRouter
from fastapi.param_functions import Body, Path
from sqlalchemy import and_, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from starlette import status

from core.app import crud
from core.depends import DatabaseSession, SellerAuthorization
from orm import SellerAddressModel, SellerAddressPhoneModel, SellerModel
from schemas import ApplicationResponse, SellerAddress
from schemas.uploads import CompanyPhoneDataRequiredUpdateUpload, SellerAddressUpload
from typing_ import RouteReturnT

router = APIRouter()


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
    seller_address_request: SellerAddressUpload,
    seller_address_phone_request: CompanyPhoneDataRequiredUpdateUpload,
) -> SellerAddressModel:
    await has_main_address_core(
        session=session,
        seller_id=seller_id,
        has_main_address=has_main_address,
        is_main=seller_address_request.is_main,
    )

    seller_address = await crud.sellers_addresses.insert.one(
        Values(
            {
                SellerAddressModel.seller_id: seller_id,
            }
            | seller_address_request.dict(),
        ),
        Returning(SellerAddressModel),
        session=session,
    )

    await crud.seller_address_phone.insert.one(
        Values(
            {SellerAddressPhoneModel.seller_address_id: seller_address.id}
            | seller_address_phone_request.dict()
        ),
        Returning(SellerAddressPhoneModel),
        session=session,
    )

    return seller_address


@router.post(
    path="/add",
    summary="WORKS: add a address for user (previously /sellers/addAddress)",
    response_model=ApplicationResponse[SellerAddress],
    status_code=status.HTTP_201_CREATED,
)
async def add_seller_address(
    user: SellerAuthorization,
    session: DatabaseSession,
    seller_address_request: SellerAddressUpload = Body(...),
    seller_address_phone_request: CompanyPhoneDataRequiredUpdateUpload = Body(...),
) -> RouteReturnT:
    return {
        "ok": True,
        "result": await add_seller_address_core(
            session=session,
            seller_id=user.seller.id,
            has_main_address=user.seller.has_main_address,
            seller_address_request=seller_address_request,
            seller_address_phone_request=seller_address_phone_request,
        ),
    }


async def update_address_core(
    session: AsyncSession,
    address_id: int,
    seller_id: int,
    has_main_address: bool,
    seller_address_request: SellerAddressUpload,
    seller_address_phone_request: CompanyPhoneDataRequiredUpdateUpload,
) -> SellerAddressModel:
    await has_main_address_core(
        session=session,
        seller_id=seller_id,
        has_main_address=has_main_address,
        is_main=seller_address_request.is_main,
    )

    seller_address = (
        await session.execute(
            update(SellerAddressModel)
            .where(
                and_(
                    SellerAddressModel.id == address_id,
                    SellerAddressModel.seller_id == seller_id,
                )
            )
            .values(seller_address_request.dict())
            .returning(SellerAddressModel)
        )
    ).scalar_one()

    await session.execute(
        update(SellerAddressPhoneModel)
        .where(SellerAddressPhoneModel.seller_address_id == seller_address.id)
        .values(seller_address_phone_request.dict())
    )

    return seller_address


@router.post(
    path="/{address_id}/update",
    summary="WORKS: update the address for user (previously /sellers/updateAddress)",
    response_model=ApplicationResponse[SellerAddress],
    status_code=status.HTTP_200_OK,
)
async def update_address(
    user: SellerAuthorization,
    session: DatabaseSession,
    address_id: int = Path(...),
    seller_address_request: SellerAddressUpload = Body(...),
    seller_address_phone_request: CompanyPhoneDataRequiredUpdateUpload = Body(...),
) -> RouteReturnT:
    return {
        "ok": True,
        "result": await update_address_core(
            session=session,
            seller_id=user.seller.id,
            has_main_address=user.seller.has_main_address,
            address_id=address_id,
            seller_address_request=seller_address_request,
            seller_address_phone_request=seller_address_phone_request,
        ),
    }


async def get_seller_addresses_core(
    session: AsyncSession,
    seller_id: int,
) -> RouteReturnT:
    return await crud.sellers_addresses.select.many(
        Where(SellerAddressModel.seller_id == seller_id),
        Options(
            selectinload(SellerAddressModel.phone).selectinload(SellerAddressPhoneModel.country),
        ),
        session=session,
    )


@router.get(
    path="",
    summary="WORKS: gets a seller addresses",
    response_model=ApplicationResponse[List[SellerAddress]],
    status_code=status.HTTP_200_OK,
)
async def get_seller_addresses(
    user: SellerAuthorization,
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
    await crud.seller_address_phone.delete.one(
        Where(and_(SellerAddressPhoneModel.seller_address_id == address_id)),
        Returning(SellerAddressPhoneModel.id),
        session=session,
    )

    await crud.sellers_addresses.delete.one(
        Where(
            and_(SellerAddressModel.id == address_id, SellerAddressModel.seller_id == seller_id)
        ),
        Returning(SellerAddressModel.id),
        session=session,
    )


@router.delete(
    path="/{address_id}/remove",
    summary="WORKS: remove user address by id (previously /sellers/removeAddress)",
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
