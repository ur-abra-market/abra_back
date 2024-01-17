from corecrud import Returning, Values, Where
from fastapi import APIRouter
from fastapi.datastructures import UploadFile
from fastapi.param_functions import Query
from sqlalchemy import and_
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from core.app import aws_s3, crud
from core.depends import DatabaseSession, Image, SupplierAuthorization
from core.exceptions import InternalServerException
from core.settings import aws_s3_settings
from orm import CompanyImageModel, CompanyModel
from schemas import ApplicationResponse, CompanyImage
from typing_ import RouteReturnT

router = APIRouter()


@router.get(
    path="/logo",
    summary="WORKS: returns company logo",
    response_model=ApplicationResponse[str],
    status_code=status.HTTP_200_OK,
)
async def get_company_logo(
    user: SupplierAuthorization,
    session: DatabaseSession,
) -> RouteReturnT:
    return {
        "ok": True,
        "result": user.supplier.company.logo_url,
    }


async def update_company_logo_core(
    session: DatabaseSession,
    company_id: int,
    file: UploadFile,
) -> str:
    link = await aws_s3.upload_file_to_s3(
        bucket_name=aws_s3_settings.S3_COMPANY_IMAGES_BUCKET, file=file
    )

    return await crud.companies.update.one(
        Values(
            {CompanyModel.logo_url: link},
        ),
        Where(CompanyModel.id == company_id),
        Returning(CompanyModel.logo_url),
        session=session,
    )


async def delete_company_logo(
    user: SupplierAuthorization,
    session: DatabaseSession,
):
    logo_url = user.supplier.company.logo_url
    if logo_url:
        try:
            await aws_s3.delete_file_from_s3(
                bucket_name=aws_s3_settings.AWS_S3_COMPANY_IMAGES_BUCKET,
                url=logo_url,
            )
            user.supplier.company.logo_url = ""
        except Exception:
            raise InternalServerException


@router.post(
    path="/logo/update",
    summary="WORKS: Uploads company logo",
    response_model=ApplicationResponse[str],
    status_code=status.HTTP_200_OK,
)
async def update_company_logo(
    file: Image,
    user: SupplierAuthorization,
    session: DatabaseSession,
) -> RouteReturnT:
    await delete_company_logo(user=user, session=session)
    return {
        "ok": True,
        "result": await update_company_logo_core(
            session=session,
            company_id=user.supplier.company.id,
            file=file,
        ),
    }


async def upload_company_image_core(
    session: AsyncSession,
    company_id: int,
    file: UploadFile,
) -> CompanyImageModel:
    link = await aws_s3.upload_file_to_s3(
        bucket_name=aws_s3_settings.S3_SUPPLIERS_PRODUCT_UPLOAD_IMAGE_BUCKET, file=file
    )

    return await crud.companies_images.insert.one(
        Values(
            {
                CompanyImageModel.company_id: company_id,
                CompanyImageModel.url: link,
            },
        ),
        Returning(CompanyImageModel),
        session=session,
    )


@router.post(
    path="/image/upload",
    summary="WORKS: Uploads provided company image to AWS S3 and saves url to DB",
    response_model=ApplicationResponse[CompanyImage],
    status_code=status.HTTP_200_OK,
)
async def upload_company_image(
    file: Image,
    user: SupplierAuthorization,
    session: DatabaseSession,
) -> RouteReturnT:
    image_urls = await crud.companies_images.delete.many(
        Where(CompanyImageModel.company_id == user.supplier.company.id),
        Returning(CompanyImageModel.url),
        session=session,
    )
    for image_url in image_urls:
        await aws_s3.delete_file_from_s3(
            bucket_name=aws_s3_settings.AWS_S3_SUPPLIERS_PRODUCT_UPLOAD_IMAGE_BUCKET,
            url=image_url,
        )
    return {
        "ok": True,
        "result": await upload_company_image_core(
            session=session,
            company_id=user.supplier.company.id,
            file=file,
        ),
    }


@router.delete(
    path="/image/delete",
    summary="WORKS: Delete provided company image from AWS S3 and url from DB",
    response_model=ApplicationResponse[bool],
    status_code=status.HTTP_200_OK,
)
async def delete_company_image(
    user: SupplierAuthorization,
    session: DatabaseSession,
    company_image_id: int = Query(...),
) -> RouteReturnT:
    image = await crud.companies_images.delete.one(
        Where(
            and_(
                CompanyImageModel.id == company_image_id,
                CompanyImageModel.company_id == user.supplier.company.id,
            ),
        ),
        Returning(CompanyImageModel.url),
        session=session,
    )

    await aws_s3.delete_file_from_s3(
        bucket_name=aws_s3_settings.S3_SUPPLIERS_PRODUCT_UPLOAD_IMAGE_BUCKET,
        url=image,
    )

    return {
        "ok": True,
        "result": True,
    }
