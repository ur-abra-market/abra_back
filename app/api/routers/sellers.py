from typing import List, Optional, Tuple

from corecrud import Options, Returning, Values, Where
from fastapi import APIRouter
from fastapi.background import BackgroundTasks
from fastapi.exceptions import HTTPException
from fastapi.param_functions import Body, Depends, Path, Query
from sqlalchemy import and_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload
from starlette import status

from core.app import aws_s3, crud
from core.depends import (
    DatabaseSession,
    FileObjects,
    Image,
    SellerAuthorization,
    seller,
)
from core.settings import aws_s3_settings
from orm import (
    OrderModel,
    SellerAddressModel,
    SellerImageModel,
    SellerModel,
    SellerNotificationsModel,
    UserModel,
)
from schemas import (
    ApplicationResponse,
    BodySellerAddressRequest,
    BodySellerAddressUpdateRequest,
    BodySellerNotificationUpdateRequest,
    OrderStatus,
    SellerAddress,
    SellerImage,
)
from typing_ import RouteReturnT
from utils.thumbnail import upload_thumbnail

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


async def update_notifications_core(
    session: AsyncSession,
    seller_id: int,
    notification_data_request: BodySellerNotificationUpdateRequest,
) -> None:
    await crud.sellers_notifications.update.one(
        Values(notification_data_request.dict()),
        Where(SellerNotificationsModel.seller_id == seller_id),
        Returning(SellerNotificationsModel.id),
        session=session,
    )


@router.patch(
    "/notifications/update/",
    summary="WORKS: update seller notifications",
    response_model=ApplicationResponse[bool],
    status_code=status.HTTP_200_OK,
)
async def update_notifications(
    user: SellerAuthorization,
    session: DatabaseSession,
    notification_data_request: BodySellerNotificationUpdateRequest = Body(...),
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


@router.get(
    path="/avatar/",
    summary="WORKS: Get logo image url from AWS S3",
    response_model=ApplicationResponse[SellerImage],
    status_code=status.HTTP_200_OK,
)
async def get_avatar_image(user: SellerAuthorization):
    return {
        "ok": True,
        "result": user.seller.image,
    }


async def upload_avatar_image_core(
    file: FileObjects,
    user: UserModel,
    session: AsyncSession,
) -> None:
    seller_image = await crud.sellers_images.select.one(
        Where(SellerImageModel.seller_id == user.seller.id),
        session=session,
    )
    link, thumbnail_link = await make_upload_and_delete_seller_images(
        seller_image=seller_image, file=file
    )

    await crud.sellers_images.update.one(
        Values(
            {SellerImageModel.source_url: link, SellerImageModel.thumbnail_url: thumbnail_link}
        ),
        Where(SellerImageModel.seller_id == user.seller.id),
        Returning(SellerImageModel.id),
        session=session,
    )


async def make_upload_and_delete_seller_images(
    seller_image: Optional[SellerImageModel],
    file: FileObjects,
) -> Tuple[str, str]:
    link = await aws_s3.upload_file_to_s3(
        bucket_name=aws_s3_settings.AWS_S3_IMAGE_USER_LOGO_BUCKET,
        file=file,
    )
    thumbnail_link = await upload_thumbnail(file=file)

    if seller_image and seller_image.source_url != link:
        await aws_s3.delete_file_from_s3(
            bucket_name=aws_s3_settings.AWS_S3_IMAGE_USER_LOGO_BUCKET,
            url=seller_image.thumbnail_url,
        )
        await aws_s3.delete_file_from_s3(
            bucket_name=aws_s3_settings.AWS_S3_IMAGE_USER_LOGO_BUCKET,
            url=seller_image.thumbnail_url,
        )

    return link, thumbnail_link


@router.post(
    path="/avatar/update/",
    summary="WORKS: Uploads provided logo image to AWS S3 and saves url to DB",
    response_model=ApplicationResponse[bool],
    status_code=status.HTTP_200_OK,
)
async def upload_avatar_image(
    file: Image,
    user: SellerAuthorization,
    session: DatabaseSession,
    background_tasks: BackgroundTasks,
) -> RouteReturnT:
    background_tasks.add_task(upload_avatar_image_core, file=file, user=user, session=session)

    return {
        "ok": True,
        "result": True,
    }
