import pathlib
from io import BytesIO
from typing import List, Tuple

from fastapi import APIRouter
from fastapi.datastructures import UploadFile
from fastapi.exceptions import HTTPException
from fastapi.param_functions import Body, Depends
from PIL import Image
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload
from starlette import status

from core.depends import (
    FileObjects,
    UserObjects,
    auth_required,
    get_session,
    image_required,
)
from core.settings import aws_s3_settings, image_settings
from core.tools import store
from orm import (
    ProductModel,
    SellerFavoriteModel,
    UserImageModel,
    UserModel,
    UserNotificationModel,
    UserSearchModel,
)
from schemas import (
    ApplicationResponse,
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
    status_code=status.HTTP_308_PERMANENT_REDIRECT,
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
    searches = await store.orm.users_searches.get_many(
        session=session,
        where=[UserSearchModel.id == user.schema.id],
        offset=pagination.offset,
        limit=pagination.limit,
    )

    return {"ok": True, "result": searches}


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
        thumb_link = await store.aws_s3.upload_file_to_s3(
            bucket=aws_s3_settings.AWS_S3_IMAGE_USER_LOGO_BUCKET,
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
    user_image: UserImageModel,
    file: FileObjects,
) -> Tuple[str, str]:
    link = await store.aws_s3.upload_file_to_s3(
        bucket_name=aws_s3_settings.AWS_S3_IMAGE_USER_LOGO_BUCKET,
        file=file,
    )
    thumbnail_link = await upload_thumbnail(file=file)

    if user_image and user_image.source_url != link:
        await store.aws_s3.delete_file_from_s3(
            bucket_name=aws_s3_settings.AWS_S3_IMAGE_USER_LOGO_BUCKET, url=user_image.thumbnail_url
        )
        await store.aws_s3.delete_file_from_s3(
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
    user_image = await store.orm.users_images.get_one(
        session=session,
        where=[UserImageModel.user_id == user.schema.id],
    )
    link, thumbnail_link = await make_upload_and_delete_user_images(
        user_image=user_image, file=file
    )

    await store.orm.users_images.update_one(
        session=session,
        values={UserImageModel.source_url: link, UserImageModel.thumbnail_url: thumbnail_link},
        where=UserImageModel.user_id == user.schema.id,
    )

    return {
        "ok": True,
        "result": True,
    }


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
        "result": await store.orm.users_notifications.get_one(
            session=session,
            where=[UserNotificationModel.user_id == user.schema.id],
        ),
    }


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
    await store.orm.users_notifications.update_one(
        session=session,
        values=request.dict(),
        where=UserNotificationModel.id == user.schema.id,
    )

    return {
        "ok": True,
        "result": True,
    }


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
    return {
        "ok": True,
        "detail": "Not worked yet",
    }


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
    await store.orm.users.update_one(
        session=session,
        values={
            UserModel.phone: request.number,
        },
        where=[UserModel.id == user.schema.id],
    )

    return {
        "ok": True,
        "result": True,
        "detail": {
            "new_phone_number": request.number,
        },
    }
