from typing import Optional, Tuple

from corecrud import Returning, Values, Where
from fastapi import APIRouter
from fastapi.background import BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from core.app import aws_s3, crud
from core.depends import DatabaseSession, FileObjects, Image, SellerAuthorization
from core.settings import aws_s3_settings
from orm import SellerImageModel, UserModel
from schemas import ApplicationResponse, SellerImage
from typing_ import RouteReturnT
from utils.thumbnail import upload_thumbnail

router = APIRouter()


@router.get(
    path="/",
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
    path="/update",
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
