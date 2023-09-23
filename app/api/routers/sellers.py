from typing import List, Optional, Tuple

from corecrud import Options, Returning, Values, Where
from fastapi import APIRouter
from fastapi.background import BackgroundTasks
from fastapi.exceptions import HTTPException
from fastapi.param_functions import Body, Depends, Path, Query
from sqlalchemy import and_, insert, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload, selectinload
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
from enums import OrderStatus as OrderStatusEnum
from orm import (
    BundleModel,
    BundleVariationModel,
    BundleVariationPodAmountModel,
    BundleVariationPodModel,
    OrderModel,
    OrderStatusHistoryModel,
    OrderStatusModel,
    SellerAddressModel,
    SellerAddressPhoneModel,
    SellerImageModel,
    SellerModel,
    SellerNotificationsModel,
    UserModel,
)
from schemas import (
    ApplicationResponse,
    Order,
    OrderStatus,
    SellerAddress,
    SellerImage,
    SellerNotifications,
)
from schemas.uploads import (
    CompanyPhoneDataRequiredUpdateUpload,
    SellerAddressUpload,
    SellerNotificationsUpdateUpload,
)
from typing_ import RouteReturnT
from utils.thumbnail import upload_thumbnail

router = APIRouter(dependencies=[Depends(seller)])


async def add_to_cart_core(
    session: AsyncSession,
    seller_id: int,
    product_id: int,
    bundle_variation_pod_id: int,
    amount: int,
) -> OrderModel:
    order = (
        (
            await session.execute(
                select(OrderModel)
                .options(
                    selectinload(OrderModel.details).joinedload(
                        BundleVariationPodAmountModel.bundle_variation_pod
                    )
                )
                .join(OrderModel.details)
                .join(BundleVariationPodAmountModel.bundle_variation_pod)
                .where(
                    OrderModel.seller_id == seller_id,
                    OrderModel.is_cart.is_(True),
                    BundleVariationPodModel.product_id == product_id,
                )
            )
        )
        .scalars()
        .unique()
        .one()
    )

    same_bundle_variation_pod = list(
        filter(lambda x: x.bundle_variation_pod_id == bundle_variation_pod_id, order.details)
    )
    if not order:
        # create an order if there's no one
        order = await crud.orders.insert.one(
            Values(
                {
                    OrderModel.seller_id: seller_id,
                    OrderModel.is_cart: True,
                }
            ),
            Returning(OrderModel),
            session=session,
        )
    elif same_bundle_variation_pod:
        # expand the bundle_variation_pod_amount if it exists
        await crud.bundles_variations_pods_amount.update.one(
            Where(
                BundleVariationPodAmountModel.bundle_variation_pod_id == bundle_variation_pod_id,
                BundleVariationPodAmountModel.order_id == order.id,
            ),
            Values(
                {
                    BundleVariationPodAmountModel.amount: order.details[0].amount + amount,
                }
            ),
            Returning(BundleVariationPodAmountModel),
            session=session,
        )
        return order

    # add bundle_variation_pod_amount to order if there's no one there
    await crud.bundles_variations_pods_amount.insert.one(
        Values(
            {
                BundleVariationPodAmountModel.bundle_variation_pod_id: bundle_variation_pod_id,
                BundleVariationPodAmountModel.order_id: order.id,
                BundleVariationPodAmountModel.amount: amount,
            }
        ),
        Returning(BundleVariationPodAmountModel),
        session=session,
    )

    return order


@router.get(
    path="/cart/add",
    summary="WORKS: Add product to cart.",
    response_model=ApplicationResponse[Order],
    status_code=status.HTTP_200_OK,
)
async def add_to_cart(
    user: SellerAuthorization,
    session: DatabaseSession,
    product_id: int = Query(),
    bundle_variation_pod_id: int = Query(),
    amount: int = Query(),
) -> RouteReturnT:
    return {
        "ok": True,
        "result": await add_to_cart_core(
            session=session,
            seller_id=user.seller.id,
            product_id=product_id,
            bundle_variation_pod_id=bundle_variation_pod_id,
            amount=amount,
        ),
    }


async def show_cart_core(
    session: AsyncSession,
    seller_id: int,
) -> List[OrderModel]:
    return await crud.orders.select.many(
        Where(
            OrderModel.seller_id == seller_id,
            OrderModel.is_cart.is_(True),
        ),
        Options(
            selectinload(OrderModel.details)
            .selectinload(BundleVariationPodAmountModel.bundle_variation_pod)
            .selectinload(BundleVariationPodModel.product),
            selectinload(OrderModel.details)
            .selectinload(BundleVariationPodAmountModel.bundle_variation_pod)
            .selectinload(BundleVariationPodModel.prices),
            selectinload(OrderModel.details)
            .selectinload(BundleVariationPodAmountModel.bundle_variation_pod)
            .selectinload(BundleVariationPodModel.bundle_variations)
            .selectinload(BundleVariationModel.bundle)
            .selectinload(BundleModel.variation_values),
        ),
        session=session,
    )


@router.get(
    path="/cart/show",
    summary="WORKS: Show seller cart.",
    response_model=ApplicationResponse[List[Order]],
    status_code=status.HTTP_200_OK,
)
async def show_cart(
    user: SellerAuthorization,
    session: DatabaseSession,
) -> RouteReturnT:
    return {
        "ok": True,
        "result": await show_cart_core(
            session=session,
            seller_id=user.seller.id,
        ),
    }


async def create_order_core(
    order_id: int,
    seller_id: int,
    session: AsyncSession,
) -> None:
    order = await crud.orders.select.one(
        Where(and_(OrderModel.id == order_id, OrderModel.seller_id == seller_id)),
        session=session,
    )

    if not order or not order.is_cart:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Specified invalid order id",
        )
    # delete order from cart
    order = await crud.orders.update.one(
        Values(
            {
                OrderModel.is_cart: False,
            }
        ),
        Where(OrderModel.id == order_id),
        Returning(OrderModel),
        session=session,
    )

    await session.execute(
        insert(OrderStatusHistoryModel).values(
            {
                OrderStatusHistoryModel.order_id: order.id,
                OrderStatusHistoryModel.order_status_id: (
                    select(OrderStatusModel.id)
                    .where(OrderStatusModel.name == OrderStatusEnum.PENDING.value)
                    .scalar_subquery()
                ),
            }
        )
    )


@router.post(
    path="/orders/{order_id}/create",
    description="Turn cart into order (after successful payment)",
    summary="WORKS: create order from a cart.",
    response_model=ApplicationResponse[bool],
    status_code=status.HTTP_200_OK,
)
async def create_order(
    user: SellerAuthorization,
    session: DatabaseSession,
    order_id: int = Path(...),
) -> RouteReturnT:
    await create_order_core(order_id=order_id, seller_id=user.seller.id, session=session)

    return {
        "ok": True,
        "result": True,
    }


@router.get(
    path="/orders/{order_id}/status",
    summary="WORKS: returns order status",
    response_model=ApplicationResponse[OrderStatus],
    status_code=status.HTTP_200_OK,
)
async def get_order_status(
    user: SellerAuthorization,
    session: DatabaseSession,
    order_id: int = Path(...),
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
    path="/addresses/add",
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

    seller_address = await crud.sellers_addresses.update.one(
        Values(seller_address_request.dict()),
        Where(
            and_(
                SellerAddressModel.id == address_id,
                SellerAddressModel.seller_id == seller_id,
            )
        ),
        Returning(SellerAddressModel),
        session=session,
    )

    await crud.seller_address_phone.update.one(
        Values(seller_address_phone_request.dict()),
        Where(and_(SellerAddressPhoneModel.seller_address_id == seller_address.id)),
        Returning(SellerAddressPhoneModel),
        session=session,
    )

    return seller_address


@router.post(
    path="/addresses/{address_id}/update",
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
    path="/addresses",
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
    path="/addresses/{address_id}/remove",
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
    "/notifications/update",
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
    "/notifications",
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


@router.get(
    path="/avatar",
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
    path="/avatar/update",
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
