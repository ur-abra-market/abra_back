from typing import List, Optional

from corecrud import (
    Join,
    Limit,
    Offset,
    Options,
    OrderBy,
    Returning,
    SelectFrom,
    Values,
    Where,
)
from fastapi import APIRouter
from fastapi.datastructures import UploadFile
from fastapi.exceptions import HTTPException
from fastapi.param_functions import Body, Depends, Path, Query
from sqlalchemy import and_, func, insert, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import join, selectinload
from starlette import status

from core.app import aws_s3, crud
from core.depends import DatabaseSession, Image, SupplierAuthorization, supplier
from core.settings import aws_s3_settings
from enums import OrderStatus as OrderStatusEnum
from orm import (
    CategoryToPropertyTypeModel,
    CategoryToVariationTypeModel,
    CompanyImageModel,
    CompanyModel,
    CompanyPhoneModel,
    OrderModel,
    OrderStatusHistoryModel,
    OrderStatusModel,
    ProductImageModel,
    ProductModel,
    PropertyValueModel,
    PropertyValueToProductModel,
    SupplierModel,
    SupplierNotificationsModel,
    UserModel,
    VariationTypeModel,
    VariationValueModel,
    VariationValueToProductModel,
    BundleVariationPodAmountModel,
    BundleVariationPodModel,
)
from schemas import (
    ApplicationResponse,
    CompanyImage,
    Product,
    ProductImage,
    ProductList,
    PropertyValue,
    Supplier,
    SupplierNotifications,
    VariationValue,
)
from schemas.uploads import (
    CompanyDataUpdateUpload,
    CompanyPhoneDataUpdateUpload,
    PaginationUpload,
    ProductEditUpload,
    ProductSortingUpload,
    ProductUpload,
    SortFilterProductsUpload,
    StatusDataUpload,
    SupplierDataUpdateUpload,
    SupplierNotificationsUpdateUpload,
)
from typing_ import RouteReturnT

router = APIRouter(dependencies=[Depends(supplier)])


@router.get(
    path="/getSupplierInfo",
    deprecated=True,
    description="Moved to /login/current/",
    summary="WORKS: Get supplier info (personal and business).",
    response_model=ApplicationResponse[Supplier],
    status_code=status.HTTP_308_PERMANENT_REDIRECT,
)
async def get_supplier_data_info(user: SupplierAuthorization) -> RouteReturnT:
    return {
        "ok": True,
        "result": user.supplier,
    }


async def get_product_properties_core(
    session: AsyncSession, category_id: int
) -> List[PropertyValue]:
    return await crud.categories_property_values.select.many(
        Where(CategoryToPropertyTypeModel.category_id == category_id),
        SelectFrom(
            join(
                PropertyValueModel,
                CategoryToPropertyTypeModel,
                PropertyValueModel.property_type_id
                == CategoryToPropertyTypeModel.property_type_id,
            )
        ),
        session=session,
    )


@router.get(
    path="/getCategoryProperties/{category_id}",
    summary="WORKS: Get all variation names and values by category_id.",
    response_model=ApplicationResponse[List[PropertyValue]],
    status_code=status.HTTP_200_OK,
)
async def get_product_properties(
    session: DatabaseSession,
    category_id: int = Path(...),
) -> RouteReturnT:
    return {
        "ok": True,
        "result": await get_product_properties_core(session=session, category_id=category_id),
    }


async def get_product_variations_core(
    session: AsyncSession, category_id: int
) -> List[VariationValue]:
    return await crud.categories_variation_values.select.many(
        Where(CategoryToVariationTypeModel.category_id == category_id),
        Options(
            selectinload(VariationValueModel.type),
        ),
        SelectFrom(
            join(
                CategoryToVariationTypeModel,
                VariationTypeModel,
                CategoryToVariationTypeModel.variation_type_id == VariationTypeModel.id,
            )
        ),
        session=session,
    )


@router.get(
    path="/getCategoryVariations/{category_id}",
    summary="WORKS (ex. 1): Get all variation names and values by category_id.",
    response_model=ApplicationResponse[List[VariationValue]],
    status_code=status.HTTP_200_OK,
)
async def get_product_variations(
    session: DatabaseSession,
    category_id: int = Path(...),
) -> RouteReturnT:
    return {
        "ok": True,
        "result": await get_product_variations_core(session=session, category_id=category_id),
    }


async def update_business_info_core(
    session: AsyncSession,
    user: UserModel,
    supplier_data_request: Optional[SupplierDataUpdateUpload],
    company_data_request: Optional[CompanyDataUpdateUpload],
    company_phone_data_request: Optional[CompanyPhoneDataUpdateUpload],
) -> None:
    if supplier_data_request:
        await crud.suppliers.update.one(
            Values(supplier_data_request.dict()),
            Where(SupplierModel.id == user.supplier.id),
            Returning(SupplierModel.id),
            session=session,
        )

    if company_data_request:
        await crud.companies.update.one(
            Values(company_data_request.dict()),
            Where(CompanyModel.supplier_id == user.supplier.id),
            Returning(CompanyModel.id),
            session=session,
        )

    if company_phone_data_request:
        if not company_phone_data_request.phone_number:
            await crud.companies_phones.delete.one(
                Where(CompanyPhoneModel.company_id == user.supplier.company.id),
                Returning(CompanyPhoneModel.id),
                session=session,
            )
        elif not user.supplier.company.phone:
            await crud.companies_phones.insert.one(
                Values(
                    {
                        **company_phone_data_request.dict(),
                        CompanyPhoneModel.company_id: user.supplier.company.id,
                    }
                ),
                Returning(CompanyPhoneModel),
                session=session,
            )
        else:
            await crud.companies_phones.update.one(
                Values(company_phone_data_request.dict()),
                Where(CompanyPhoneModel.company_id == user.supplier.company.id),
                Returning(CompanyPhoneModel.id),
                session=session,
            )


@router.post(
    path="/businessInfo/update",
    summary="WORKS: update SupplierModel existing information licence information & CompanyModel information",
    response_model=ApplicationResponse[bool],
    status_code=status.HTTP_200_OK,
)
async def update_business_info(
    user: SupplierAuthorization,
    session: DatabaseSession,
    supplier_data_request: Optional[SupplierDataUpdateUpload] = Body(None),
    company_data_request: Optional[CompanyDataUpdateUpload] = Body(None),
    company_phone_data_request: Optional[CompanyPhoneDataUpdateUpload] = Body(None),
) -> RouteReturnT:
    await update_business_info_core(
        session=session,
        user=user,
        supplier_data_request=supplier_data_request,
        company_data_request=company_data_request,
        company_phone_data_request=company_phone_data_request,
    )

    return {
        "ok": True,
        "result": True,
    }


async def get_business_info_core(
    session: AsyncSession,
    supplier_id: int,
) -> Supplier:
    return await crud.suppliers.select.one(
        Where(SupplierModel.id == supplier_id),
        Options(
            selectinload(SupplierModel.company).selectinload(CompanyModel.country),
            selectinload(SupplierModel.company)
            .selectinload(CompanyModel.phone)
            .selectinload(CompanyPhoneModel.country),
        ),
        session=session,
    )


@router.get(
    path="/businessInfo",
    summary="WORKS: return company and supplier info",
    response_model=ApplicationResponse[Supplier],
    response_model_exclude={
        "result": {"notifications": ..., "company": {"logo_url"}},
    },
    status_code=status.HTTP_200_OK,
)
async def get_business_info(
    user: SupplierAuthorization,
    session: DatabaseSession,
) -> RouteReturnT:
    return {
        "ok": True,
        "result": await get_business_info_core(session=session, supplier_id=user.supplier.id),
    }


@router.get(
    path="/companyLogo",
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
        bucket_name=aws_s3_settings.AWS_S3_COMPANY_IMAGES_BUCKET, file=file
    )

    return await crud.companies.update.one(
        Values(
            {CompanyModel.logo_url: link},
        ),
        Where(CompanyModel.id == company_id),
        Returning(CompanyModel.logo_url),
        session=session,
    )


@router.post(
    path="/companyLogo/update",
    summary="WORKS: Uploads company logo",
    response_model=ApplicationResponse[str],
    status_code=status.HTTP_200_OK,
)
async def update_company_logo(
    file: Image,
    user: SupplierAuthorization,
    session: DatabaseSession,
) -> RouteReturnT:
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
        bucket_name=aws_s3_settings.AWS_S3_SUPPLIERS_PRODUCT_UPLOAD_IMAGE_BUCKET, file=file
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
    path="/uploadCompanyImage",
    summary="WORKS: Uploads provided company image to AWS S3 and saves url to DB",
    response_model=ApplicationResponse[CompanyImage],
    status_code=status.HTTP_200_OK,
)
async def upload_company_image(
    file: Image,
    user: SupplierAuthorization,
    session: DatabaseSession,
) -> RouteReturnT:
    return {
        "ok": True,
        "result": await upload_company_image_core(
            session=session,
            company_id=user.supplier.company.id,
            file=file,
        ),
    }


@router.delete(
    path="/deleteCompanyImage",
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
        bucket_name=aws_s3_settings.AWS_S3_SUPPLIERS_PRODUCT_UPLOAD_IMAGE_BUCKET,
        url=image,
    )

    return {
        "ok": True,
        "result": True,
    }


async def update_notifications_core(
    session: AsyncSession,
    supplier_id: int,
    notification_data_request: Optional[SupplierNotificationsUpdateUpload],
) -> None:
    if notification_data_request:
        await crud.suppliers_notifications.update.one(
            Values(notification_data_request.dict()),
            Where(SupplierNotificationsModel.supplier_id == supplier_id),
            Returning(SupplierNotificationsModel.id),
            session=session,
        )


@router.post(
    path="/notifications/update",
    summary="WORKS: update notifications for supplier",
    response_model=ApplicationResponse[bool],
    status_code=status.HTTP_200_OK,
)
async def update_notifications(
    user: SupplierAuthorization,
    session: DatabaseSession,
    notification_data_request: Optional[SupplierNotificationsUpdateUpload] = Body(None),
) -> RouteReturnT:
    await update_notifications_core(
        session=session,
        supplier_id=user.supplier.id,
        notification_data_request=notification_data_request,
    )

    return {
        "ok": True,
        "result": True,
    }


async def get_notifications_core(
    session: AsyncSession,
    supplier_id: int,
) -> SupplierNotificationsModel:
    return await crud.suppliers_notifications.select.one(
        Where(SupplierNotificationsModel.supplier_id == supplier_id),
        session=session,
    )


@router.get(
    "/notifications",
    summary="WORKS: get supplier notifications",
    response_model=ApplicationResponse[SupplierNotifications],
    status_code=status.HTTP_200_OK,
)
async def get_notifications(
    user: SupplierAuthorization,
    session: DatabaseSession,
) -> RouteReturnT:
    return {
        "ok": True,
        "result": await get_notifications_core(session=session, supplier_id=user.supplier.id),
    }


@router.get(
    path="/hasBusinessInfo",
    summary="WORKS: get Company info",
    response_model=ApplicationResponse[bool],
    status_code=status.HTTP_200_OK,
)
def has_business_info(user: SupplierAuthorization) -> RouteReturnT:
    return {"ok": True, "result": bool(user.supplier.company)}


@router.get(
    path="/hasPersonalInfo",
    summary="WORKS: get Personal info",
    response_model=ApplicationResponse[bool],
    status_code=status.HTTP_200_OK,
)
def has_personal_info(user: SupplierAuthorization) -> RouteReturnT:
    return {"ok": True, "result": bool(user.first_name)}
