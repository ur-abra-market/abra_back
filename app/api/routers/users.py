from io import BytesIO
from typing import List, Optional, Tuple

from fastapi import APIRouter
from fastapi.background import BackgroundTasks
from fastapi.datastructures import UploadFile
from fastapi.exceptions import HTTPException
from fastapi.param_functions import Body, Depends, Query
from PIL import Image as PILImage
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from starlette import status

from core.app import aws_s3, crud
from core.depends import (
    Authorization,
    DatabaseSession,
    FileObjects,
    Image,
    SupplierAuthorization,
)
from core.settings import aws_s3_settings, user_settings
from orm import (
    CompanyModel,
    ProductModel,
    SellerFavoriteModel,
    SellerImageModel,
    SupplierModel,
    UserModel,
    UserNotificationModel,
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

router = APIRouter()


async def get_latest_searches_core(
    session: AsyncSession, user_id: int, offset: int, limit: int
) -> List[UserSearch]:
    return await crud.users_searches.get_many_by(
        session=session,
        user_id=user_id,
        offset=offset,
        limit=limit,
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
    seller_image = await crud.sellers_images.get.one(
        session=session,
        where=[SellerImageModel.seller_id == user.seller.id],
    )
    link, thumbnail_link = await make_upload_and_delete_seller_images(
        seller_image=seller_image, file=file
    )

    await crud.sellers_images.update.one(
        session=session,
        values={SellerImageModel.source_url: link, SellerImageModel.thumbnail_url: thumbnail_link},
        where=SellerImageModel.seller_id == user.seller.id,
    )


@router.post(
    path="/uploadLogoImage/",
    summary="WORKS: Uploads provided logo image to AWS S3 and saves url to DB",
    response_model=ApplicationResponse[bool],
    status_code=status.HTTP_200_OK,
)
async def upload_logo_image(
    file: Image,
    user: Authorization,
    session: DatabaseSession,
    background_tasks: BackgroundTasks,
) -> RouteReturnT:
    if not user.seller:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Seller not found")

    background_tasks.add_task(upload_logo_image_core, file=file, user=user, session=session)

    return {
        "ok": True,
        "result": True,
    }


async def get_notifications_core(session: AsyncSession, user_id: int) -> UserNotificationModel:
    return await crud.users_notifications.get.one(
        session=session,
        where=[UserNotificationModel.user_id == user_id],
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
) -> None:
    await crud.users_notifications.update.one(
        session=session,
        values=request.dict(),
        where=UserNotificationModel.id == user_id,
    )


@router.patch(
    path="/updateNotifications/",
    summary="WORKS: Displaying the notification switch",
    response_model=ApplicationResponse[bool],
    status_code=status.HTTP_200_OK,
)
async def update_notifications(
    user: Authorization,
    session: DatabaseSession,
    request: BodyUserNotificationRequest = Body(...),
) -> RouteReturnT:
    await update_notifications_core(
        session=session,
        user_id=user.id,
        request=request,
    )

    return {
        "ok": True,
        "result": True,
    }


async def show_favorites_core(
    session: AsyncSession,
    seller_id: int,
    offset: int,
    limit: int,
) -> List[ProductModel]:
    favorites = await crud.raws.get.many(
        SellerFavoriteModel.id,
        session=session,
        where=[SellerFavoriteModel.seller_id == seller_id],
        select_from=[SellerFavoriteModel],
    )

    return await crud.products.get.many(
        session=session,
        where=[ProductModel.id.in_(favorites)],
        options=[
            selectinload(ProductModel.category),
            selectinload(ProductModel.tags),
            selectinload(ProductModel.prices),
        ],
        offset=offset,
        limit=limit,
    )


@router.get(
    path="/showFavorites/",
    summary="WORKS: Shows all favorite products",
    response_model=ApplicationResponse[List[Product]],
    status_code=status.HTTP_200_OK,
)
async def show_favorites(
    user: Authorization,
    session: DatabaseSession,
    pagination: QueryPaginationRequest = Depends(),
) -> RouteReturnT:
    if not user.seller:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Seller required")

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
        session=session,
        values={
            UserModel.email: email,
        },
        where=UserModel.id == user_id,
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
    await crud.phone_numbers.update.one(
        session=session,
        values=request.dict(),
        where=UserModel.id == user_id,
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
    user: Authorization,
    session: DatabaseSession,
    product_id: int = Query(...),
) -> RouteReturnT:
    if not user.seller:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Seller required",
        )

    seller_favorite = await crud.sellers_favorites.get.one(
        session=session,
        where=[
            SellerFavoriteModel.seller_id == user.seller.id,
            SellerFavoriteModel.product_id == product_id,
        ],
    )

    return {"ok": True, "result": bool(seller_favorite)}


async def update_acount_info_core(
    session: AsyncSession,
    user_id: int,
    request: BodyUserDataUpdateRequest,
) -> None:
    await crud.users.update.one(
        session=session, values=request.dict(), where=UserModel.id == user_id
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
    await update_acount_info_core(session=session, user_id=user.id, request=request)

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
        session=session, values=supplier_data_request.dict(), where=SupplierModel.id == supplier_id
    )

    await crud.companies.insert.one(
        session=session,
        values={
            CompanyModel.supplier_id: supplier_id,
        }
        | company_data_request.dict(),
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
