from io import BytesIO
from typing import Any, List, Optional, Tuple

from corecrud import (
    GroupBy,
    Join,
    Limit,
    Offset,
    Options,
    OuterJoin,
    Returning,
    SelectFrom,
    Values,
    Where,
)
from fastapi import APIRouter
from fastapi.background import BackgroundTasks
from fastapi.datastructures import UploadFile
from fastapi.param_functions import Body, Depends, Query
from fastapi.responses import Response
from PIL import Image as PILImage
from sqlalchemy import and_, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from starlette import status

from core.app import aws_s3, crud
from core.depends import (
    AuthJWT,
    Authorization,
    DatabaseSession,
    FileObjects,
    Image,
    SellerAuthorization,
    SupplierAuthorization,
)
from core.settings import aws_s3_settings, user_settings
from orm import (
    CompanyModel,
    OrderModel,
    OrderProductVariationModel,
    OrderStatusModel,
    ProductImageModel,
    ProductModel,
    ProductPriceModel,
    ProductVariationCountModel,
    ProductVariationValueModel,
    SellerFavoriteModel,
    SellerImageModel,
    SupplierModel,
    UserModel,
    UserNotificationModel,
    UserSearchModel,
)
from schemas import (
    ApplicationResponse,
    BodyChangeEmailRequest,
    BodyCompanyDataUpdateRequest,
    BodyPhoneNumberRequest,
    BodySupplierDataRequest,
    BodyUserDataUpdateRequest,
    BodyUserNotificationRequest,
    Product,
    QueryPaginationRequest,
    UserNotification,
    UserSearch,
)
from typing_ import RouteReturnT
from utils.cookies import unset_jwt_cookies

router = APIRouter()


async def get_latest_searches_core(
    session: AsyncSession, user_id: int, offset: int, limit: int
) -> List[UserSearch]:
    return await crud.users_searches.select.many(
        Where(UserSearchModel.user_id == user_id), Offset(offset), Limit(limit), session=session
    )


@router.get(
    path="/latestSearches/",
    summary="WORKS (example 5): Get latest searches by user_id.",
    response_model=ApplicationResponse[List[UserSearch]],
    status_code=status.HTTP_200_OK,
)
async def get_latest_searches(
    user: Authorization,
    session: DatabaseSession,
    pagination: QueryPaginationRequest = Depends(),
) -> RouteReturnT:
    return {
        "ok": True,
        "result": await get_latest_searches_core(
            session=session,
            user_id=user.id,
            offset=pagination.offset,
            limit=pagination.limit,
        ),
    }


def thumbnail(contents: bytes, content_type: str) -> BytesIO:
    io = BytesIO()
    image = PILImage.open(BytesIO(contents))
    image.thumbnail((user_settings.USER_LOGO_THUMBNAIL_X, user_settings.USER_LOGO_THUMBNAIL_Y))
    image.save(io, format=content_type)
    io.seek(0)
    return io


async def upload_thumbnail(file: FileObjects) -> str:
    io = thumbnail(contents=file.contents, content_type=file.source.content_type.split("/")[-1])
    try:
        thumb_link = await aws_s3.upload_file_to_s3(
            bucket_name=aws_s3_settings.AWS_S3_IMAGE_USER_LOGO_BUCKET,
            file=FileObjects(
                contents=io.getvalue(),
                source=UploadFile(
                    file=io,
                    size=io.getbuffer().nbytes,
                    filename=file.source.filename,
                    headers=file.source.headers,
                ),
            ),
        )
    except Exception:
        io.close()
        raise

    return thumb_link


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


async def upload_logo_image_core(
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


@router.post(
    path="/uploadLogoImage/",
    summary="WORKS: Uploads provided logo image to AWS S3 and saves url to DB",
    response_model=ApplicationResponse[bool],
    status_code=status.HTTP_200_OK,
)
async def upload_logo_image(
    file: Image,
    user: SellerAuthorization,
    session: DatabaseSession,
    background_tasks: BackgroundTasks,
) -> RouteReturnT:
    background_tasks.add_task(upload_logo_image_core, file=file, user=user, session=session)

    return {
        "ok": True,
        "result": True,
    }


async def get_notifications_core(session: AsyncSession, user_id: int) -> UserNotificationModel:
    return await crud.users_notifications.select.one(
        Where(UserNotificationModel.user_id == user_id),
        session=session,
    )


@router.get(
    path="/getNotifications/",
    summary="WORKS: Displaying the notification switch",
    response_model=ApplicationResponse[UserNotification],
    status_code=status.HTTP_200_OK,
)
async def get_notifications(
    user: Authorization,
    session: DatabaseSession,
) -> RouteReturnT:
    return {
        "ok": True,
        "result": await get_notifications_core(session=session, user_id=user.id),
    }


async def update_notifications_core(
    session: AsyncSession, user_id: int, request: BodyUserNotificationRequest
) -> UserNotificationModel:
    return await crud.users_notifications.update.one(
        Values(request.dict()),
        Where(UserNotificationModel.user_id == user_id),
        Returning(UserNotificationModel),
        session=session,
    )


@router.patch(
    path="/updateNotifications/",
    summary="WORKS: Displaying the notification switch",
    response_model=ApplicationResponse[UserNotification],
    status_code=status.HTTP_200_OK,
)
async def update_notifications(
    user: Authorization,
    session: DatabaseSession,
    request: BodyUserNotificationRequest = Body(...),
) -> RouteReturnT:
    return {
        "ok": True,
        "result": await update_notifications_core(
            session=session,
            user_id=user.id,
            request=request,
        ),
    }


async def show_favorites_core(
    session: AsyncSession,
    seller_id: int,
    offset: int,
    limit: int,
) -> List[ProductModel]:
    favorites = await crud.raws.select.many(
        Where(SellerFavoriteModel.seller_id == seller_id),
        SelectFrom(SellerFavoriteModel),
        nested_select=[SellerFavoriteModel.id],
        session=session,
    )

    return await crud.products.select.many(
        Where(ProductModel.id.in_(favorites)),
        Options(
            selectinload(ProductModel.category),
            selectinload(ProductModel.tags),
            selectinload(ProductModel.prices),
        ),
        Offset(offset),
        Limit(limit),
        session=session,
    )


@router.get(
    path="/showFavorites/",
    summary="WORKS: Shows all favorite products",
    response_model=ApplicationResponse[List[Product]],
    status_code=status.HTTP_200_OK,
)
async def show_favorites(
    user: SellerAuthorization,
    session: DatabaseSession,
    pagination: QueryPaginationRequest = Depends(),
) -> RouteReturnT:
    return {
        "ok": True,
        "result": await show_favorites_core(
            session=session,
            seller_id=user.seller.id,
            offset=pagination.offset,
            limit=pagination.limit,
        ),
    }


async def change_email_core(
    session: AsyncSession,
    user_id: int,
    email: str,
) -> None:
    await crud.users.update.one(
        Values(
            {
                UserModel.email: email,
            }
        ),
        Where(UserModel.id == user_id),
        Returning(UserModel.id),
        session=session,
    )


@router.patch(
    path="/changeEmail",
    summary="WORKS: allows user to change his email",
    response_model=ApplicationResponse[bool],
    status_code=status.HTTP_200_OK,
)
async def change_email(
    user: Authorization,
    session: DatabaseSession,
    request: BodyChangeEmailRequest = Body(...),
) -> RouteReturnT:
    await change_email_core(
        session=session,
        user_id=user.id,
        email=request.confirm_email,
    )

    return {
        "ok": True,
        "result": True,
    }


async def change_phone_number_core(
    session: AsyncSession,
    user_id: int,
    request: BodyPhoneNumberRequest,
) -> None:
    await crud.users.update.one(
        Values(request.dict()),
        Where(UserModel.id == user_id),
        session=session,
    )


@router.patch(
    path="/changePhoneNumber/",
    summary="WORKS: Allows user to change his phone number",
    response_model=ApplicationResponse[bool],
    status_code=status.HTTP_200_OK,
)
async def change_phone_number(
    user: Authorization,
    session: DatabaseSession,
    request: BodyPhoneNumberRequest = Body(...),
) -> RouteReturnT:
    await change_phone_number_core(
        session=session,
        user_id=user.id,
        request=request,
    )

    return {
        "ok": True,
        "result": True,
    }


@router.get(
    path="/isFavorite",
    summary="WORKS: returns is product in favorites",
    response_model=ApplicationResponse[bool],
    status_code=status.HTTP_200_OK,
)
async def is_product_favorite(
    user: SellerAuthorization,
    session: DatabaseSession,
    product_id: int = Query(...),
) -> RouteReturnT:
    seller_favorite = await crud.sellers_favorites.select.one(
        Where(
            SellerFavoriteModel.seller_id == user.seller.id,
            SellerFavoriteModel.product_id == product_id,
        ),
        session=session,
    )

    return {
        "ok": True,
        "result": bool(seller_favorite),
    }


async def update_account_info_core(
    session: AsyncSession,
    user_id: int,
    request: BodyUserDataUpdateRequest,
) -> None:
    await crud.users.update.one(
        Values(request.dict()),
        Where(UserModel.id == user_id),
        Returning(UserModel.id),
        session=session,
    )


@router.patch(
    path="/account/update/",
    summary="WORKS: updated UserModel information such as: first_name, last_name, country_code, phone_number",
    response_model=ApplicationResponse[bool],
    status_code=status.HTTP_200_OK,
)
async def update_account_info(
    user: Authorization,
    session: DatabaseSession,
    request: BodyUserDataUpdateRequest = Body(...),
) -> RouteReturnT:
    await update_account_info_core(session=session, user_id=user.id, request=request)

    return {
        "ok": True,
        "result": True,
    }


async def delete_account_core(session: AsyncSession, user_id: int) -> None:
    await crud.users.update.one(
        Values({UserModel.is_deleted: 1}),
        Where(UserModel.id == user_id),
        Returning(UserModel.id),
        session=session,
    )


@router.delete(
    path="/account/delete/",
    summary="WORKS: Delete user account.",
    response_model=ApplicationResponse[bool],
    status_code=status.HTTP_200_OK,
)
async def delete_account(
    response: Response,
    authorize: AuthJWT,
    user: Authorization,
    session: DatabaseSession,
) -> RouteReturnT:
    await delete_account_core(session=session, user_id=user.id)
    unset_jwt_cookies(response=response, authorize=authorize)

    return {
        "ok": True,
        "result": True,
    }


async def update_business_info_core(
    session: AsyncSession,
    supplier_id: int,
    supplier_data_request: BodySupplierDataRequest,
    company_data_request: BodyCompanyDataUpdateRequest,
) -> None:
    await crud.suppliers.update.one(
        Values(supplier_data_request.dict()),
        Where(SupplierModel.id == supplier_id),
        Returning(SupplierModel.id),
        session=session,
    )

    await crud.companies.insert.one(
        Values(
            {
                CompanyModel.supplier_id: supplier_id,
            }
            | company_data_request.dict(),
        ),
        Returning(CompanyModel.id),
        session=session,
    )


@router.patch(
    path="/business/update/",
    summary="WORKS: update SupplierModel existing information licence information & CompanyModel information",
    response_model=ApplicationResponse[bool],
    status_code=status.HTTP_200_OK,
)
async def insert_business_info(
    user: SupplierAuthorization,
    session: DatabaseSession,
    supplier_data_request: BodySupplierDataRequest = Body(...),
    company_data_request: BodyCompanyDataUpdateRequest = Body(...),
) -> RouteReturnT:
    await update_business_info_core(
        session=session,
        supplier_id=user.supplier.id,
        supplier_data_request=supplier_data_request,
        company_data_request=company_data_request,
    )

    return {
        "ok": True,
        "result": True,
    }


async def get_seller_orders_core(
    session: AsyncSession,
    seller_id: int,
) -> List[Any]:
    return await crud.raws.select.many(
        Where(
            OrderModel.seller_id == seller_id,
        ),
        Join(
            OrderStatusModel,
            OrderModel.status_id == OrderStatusModel.id,
        ),
        Join(
            OrderProductVariationModel,
            OrderModel.id == OrderProductVariationModel.order_id,
        ),
        Join(
            ProductVariationCountModel,
            ProductVariationCountModel.id == OrderProductVariationModel.product_variation_count_id,
        ),
        Join(
            ProductVariationValueModel,
            ProductVariationCountModel.product_variation_value1_id
            == ProductVariationValueModel.id,
        ),
        Join(ProductModel, ProductModel.id == ProductVariationValueModel.product_id),
        Join(ProductPriceModel, ProductPriceModel.product_id == ProductModel.id),
        OuterJoin(
            ProductImageModel,
            and_(
                ProductImageModel.product_id == ProductVariationValueModel.product_id,
            ),
        ),
        GroupBy(
            OrderModel.id,
            OrderModel.seller_id,
            ProductModel.id,
            ProductPriceModel.value,
            OrderStatusModel.name,
        ),
        nested_select=[
            OrderModel.id.label("order_id"),
            OrderModel.seller_id,
            ProductModel.id.label("product_id"),
            ProductPriceModel.value.label("price_value"),
            func.array_agg(ProductImageModel.image_url).label("product_image_urls"),
            OrderStatusModel.name.label("status_name"),
        ],
        session=session,
    )


@router.get(
    path="/orders/",
    summary="WORKS: get list of orders of a particular user",
    response_model=ApplicationResponse[List[RouteReturnT]],
    status_code=status.HTTP_200_OK,
)
async def get_seller_orders(
    user: SellerAuthorization,
    session: DatabaseSession,
) -> RouteReturnT:
    return {
        "ok": True,
        "result": await get_seller_orders_core(
            session=session,
            seller_id=user.seller.id,
        ),
    }
