# mypy: disable-error-code="arg-type,return-value,no-any-return"

from io import BytesIO
from typing import List, Optional, Tuple

from fastapi import APIRouter
from fastapi.datastructures import UploadFile
from fastapi.exceptions import HTTPException
from fastapi.param_functions import Body, Depends
from PIL import Image
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload
from starlette import status

from core.aws_s3 import aws_s3
from core.depends import (
    FileObjects,
    UserObjects,
    auth_required,
    get_session,
    image_required,
)
from core.orm import orm
from core.settings import aws_s3_settings, image_settings
from orm import (
    ProductModel,
    SellerFavoriteModel,
    UserImageModel,
    UserModel,
    UserNotificationModel,
)
from schemas import (
    ApplicationResponse,
    BodyChangeEmailRequest,
    BodyPhoneNumberRequest,
    BodyUserNotificationRequest,
    Product,
    QueryPaginationRequest,
    User,
    UserNotification,
    UserSearch,
)

router = APIRouter()


@router.get(
    path="/getMe/",
    summary="WORKS: Get user role.",
    response_model=ApplicationResponse[User],
    status_code=status.HTTP_200_OK,
)
@router.get(
    path="/get_role/",
    description="Moved to /users/getMe",
    deprecated=True,
    summary="WORKS: Get user role.",
    response_model=ApplicationResponse[User],
    status_code=status.HTTP_308_PERMANENT_REDIRECT,
)
async def get_user_role(
    user: UserObjects = Depends(auth_required),
) -> ApplicationResponse[User]:
    return {"ok": True, "result": user.schema}


async def get_latest_searches_core(
    session: AsyncSession, user_id: int, offset: int, limit: int
) -> List[UserSearch]:
    return await orm.users_searches.get_many_by(
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
@router.get(
    path="/latest_searches/",
    description="Moved to /users/latestSearches",
    deprecated=True,
    summary="WORKS (example 5): Get latest searches by user_id.",
    response_model=ApplicationResponse[List[UserSearch]],
    status_code=status.HTTP_308_PERMANENT_REDIRECT,
)
async def get_latest_searches(
    pagination: QueryPaginationRequest = Depends(),
    user: UserObjects = Depends(auth_required),
    session: AsyncSession = Depends(get_session),
) -> ApplicationResponse[List[UserSearch]]:
    return {
        "ok": True,
        "result": await get_latest_searches_core(
            session=session,
            user_id=user.schema.id,
            offset=pagination.offset,
            limit=pagination.limit,
        ),
    }


def thumbnail(contents: bytes, content_type: str) -> BytesIO:
    io = BytesIO()
    image = Image.open(BytesIO(contents))
    image.thumbnail(image_settings.USER_LOGO_THUMBNAIL_SIZE)
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


async def make_upload_and_delete_user_images(
    user_image: Optional[UserImageModel],
    file: FileObjects,
) -> Tuple[str, str]:
    link = await aws_s3.upload_file_to_s3(
        bucket_name=aws_s3_settings.AWS_S3_IMAGE_USER_LOGO_BUCKET,
        file=file,
    )
    thumbnail_link = await upload_thumbnail(file=file)

    if user_image and user_image.source_url != link:
        await aws_s3.delete_file_from_s3(
            bucket_name=aws_s3_settings.AWS_S3_IMAGE_USER_LOGO_BUCKET, url=user_image.thumbnail_url
        )
        await aws_s3.delete_file_from_s3(
            bucket_name=aws_s3_settings.AWS_S3_IMAGE_USER_LOGO_BUCKET, url=user_image.thumbnail_url
        )

    return link, thumbnail_link


@router.post(
    path="/uploadLogoImage/",
    summary="WORKS: Uploads provided logo image to AWS S3 and saves url to DB",
    response_model=ApplicationResponse[bool],
    status_code=status.HTTP_200_OK,
)
@router.post(
    path="/upload_logo_image/",
    description="Moved to /users/uploadLogoImage",
    deprecated=True,
    summary="WORKS: Uploads provided logo image to AWS S3 and saves url to DB",
    response_model=ApplicationResponse[bool],
    status_code=status.HTTP_308_PERMANENT_REDIRECT,
)
async def upload_logo_image(
    file: FileObjects = Depends(image_required),
    user: UserObjects = Depends(auth_required),
    session: AsyncSession = Depends(get_session),
) -> ApplicationResponse[bool]:
    user_image = await orm.users_images.get_one_by(
        session=session,
        user_id=user.schema.id,
    )
    link, thumbnail_link = await make_upload_and_delete_user_images(
        user_image=user_image, file=file
    )

    await orm.users_images.update_one(
        session=session,
        values={UserImageModel.source_url: link, UserImageModel.thumbnail_url: thumbnail_link},
        where=UserImageModel.user_id == user.schema.id,
    )

    return {
        "ok": True,
        "result": True,
    }


async def get_notifications_core(session: AsyncSession, user_id: int) -> UserNotificationModel:
    return await orm.users_notifications.get_one_by(
        session=session,
        user_id=user_id,
    )


@router.get(
    path="/getNotifications/",
    summary="WORKS: Displaying the notification switch",
    response_model=ApplicationResponse[UserNotification],
    status_code=status.HTTP_200_OK,
)
@router.get(
    path="/get_notifications/",
    description="Moved to /users/getNotifications",
    deprecated=True,
    summary="WORKS: Displaying the notification switch",
    response_model=ApplicationResponse[UserNotification],
    status_code=status.HTTP_308_PERMANENT_REDIRECT,
)
async def get_notifications(
    user: UserObjects = Depends(auth_required), session: AsyncSession = Depends(get_session)
) -> ApplicationResponse[UserNotification]:
    return {
        "ok": True,
        "result": await get_notifications_core(session=session, user_id=user.schema.id),
    }


async def update_notifications_core(
    session: AsyncSession, user_id: int, request: BodyUserNotificationRequest
) -> None:
    await orm.users_notifications.update_one(
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
@router.patch(
    path="/update_notification/",
    description="Moved to /users/updateNotifications",
    deprecated=True,
    summary="WORKS: Displaying the notification switch",
    response_model=ApplicationResponse[bool],
    status_code=status.HTTP_308_PERMANENT_REDIRECT,
)
async def update_notifications(
    request: BodyUserNotificationRequest = Body(...),
    user: UserObjects = Depends(auth_required),
    session: AsyncSession = Depends(get_session),
) -> ApplicationResponse[bool]:
    await update_notifications_core(
        session=session,
        user_id=user.schema.id,
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
    favorites = await orm.raws.get_many(
        SellerFavoriteModel.id,
        session=session,
        where=[SellerFavoriteModel.seller_id == seller_id],
        select_from=[SellerFavoriteModel],
    )
    if not favorites:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Favorites products not found"
        )

    return await orm.products.get_many_unique(
        session=session,
        where=[ProductModel.id.in_(favorites)],
        options=[
            joinedload(ProductModel.category),
            joinedload(ProductModel.tags),
            joinedload(ProductModel.prices),
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
@router.get(
    path="/show_favorites/",
    description="Moved to /users/showFavorites",
    deprecated=True,
    summary="WORKS: Shows all favorite products",
    response_model=ApplicationResponse[List[Product]],
    status_code=status.HTTP_308_PERMANENT_REDIRECT,
)
async def show_favorites(
    pagination: QueryPaginationRequest = Depends(),
    user: UserObjects = Depends(auth_required),
    session: AsyncSession = Depends(get_session),
) -> ApplicationResponse[List[Product]]:
    if not user.orm.seller:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Seller required")

    return {
        "ok": True,
        "result": await show_favorites_core(
            session=session,
            seller_id=user.schema.seller.id,
            offset=pagination.offset,
            limit=pagination.limit,
        ),
    }


async def change_email_core(
    session: AsyncSession,
    user_id: int,
    email: str,
) -> None:
    await orm.users.update_one(
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
@router.patch(
    path="/change_email",
    description="Moved to /users/changeEmail",
    deprecated=True,
    summary="WORKS: allows user to change his email",
    response_model=ApplicationResponse[bool],
    status_code=status.HTTP_308_PERMANENT_REDIRECT,
)
async def change_email(
    request: BodyChangeEmailRequest = Body(...),
    user: UserObjects = Depends(auth_required),
    session: AsyncSession = Depends(get_session),
) -> ApplicationResponse[bool]:
    await change_email_core(
        session=session,
        user_id=user.schema.id,
        email=request.confirm_email,
    )

    return {
        "ok": True,
        "result": True,
    }


async def change_phone_number_core(
    session: AsyncSession,
    user_id: int,
    number: str,
) -> None:
    await orm.users.update_one(
        session=session,
        values={
            UserModel.phone: number,
        },
        where=UserModel.id == user_id,
    )


@router.patch(
    path="/changePhoneNumber/",
    summary="WORKS: Allows user to change his phone number",
    response_model=ApplicationResponse[bool],
    status_code=status.HTTP_200_OK,
)
@router.patch(
    path="/change_phone_number/",
    description="Moved to /users/changePhoneNumber",
    deprecated=True,
    summary="WORKS: Allows user to change his phone number",
    response_model=ApplicationResponse[bool],
    status_code=status.HTTP_308_PERMANENT_REDIRECT,
)
async def change_phone_number(
    request: BodyPhoneNumberRequest = Body(...),
    user: UserObjects = Depends(auth_required),
    session: AsyncSession = Depends(get_session),
) -> ApplicationResponse[bool]:
    await change_phone_number_core(
        session=session,
        user_id=user.schema.id,
        number=request.number,
    )

    return {
        "ok": True,
        "result": True,
        "detail": {
            "new_phone_number": request.number,
        },
    }
